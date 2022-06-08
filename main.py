import asyncio
from bleak import BleakClient, BleakScanner
from tkinter import *
from datetime import datetime
import threading
import random
import protocol

#asyncio
root = None

# connect ble
write_characteristic = None
read_characteristic = None
read_write_charcteristic_uuid = "f0001111-0451-4000-b000-000000000000"
ble_client = None
ble_connect = False
ble_program_type = -1


#ui
#연결 전 ui
devicelistbox = None
scan_btn = None
connect_btn = None
frame = None
scan_stop_btn = None
scrollbar = None
devicelistbox = None
text = None
#연결 후 ui
close_btn = None
measure_btn = None
stop_btn = None
get_hr_btn = None
get_spo2_btn = None
random_btn = None
write_label = None
read_label = None
label = None
text = None
submit_btn = None

# label text
read_text = None
write_text = None
status_text = None

# scan
devicelistnum = 0
devicelist = []
scanner = None
scanning = True
select_address = None

# read ble 
real_read_packet = []
check_flag = 0
read_len_str = ""
read_len = -2

"""
print function
"""
def print_hex(data):
    hex_data = None
    for i in list(data):
        hex_data += hex(i)+" "
    return hex_data

def write_label_set(data):
    global write_text
    write_text.set(f"WRITE DATA : {data}")

def read_label_set(data):
    global read_text    
    read_text.set(f"READ DATA : {data}")

def status_label_set(data):
    global status_text
    status_text.set(data)
"""
communication function
"""
def ble_read_init():
    global check_flag, real_read_packet,read_len_str, read_len
    check_flag = 0
    read_len_str = ""
    read_len = -2
    real_read_packet = []

async def ble_read():
    global read_characteristic, check_flag, real_read_packet,read_len_str, read_len
    read = await ble_client.read_gatt_char(read_characteristic)
    print("[BLE] Read ! : ", read)
    
    read_list = list(read)
    for i in range(len(read_list)):
        if read_list[i] == 2 and (read_list[i+1] == 56 or read_list[i+1] == 57) :
            check_flag = 1
            real_read_packet.append(read_list[i])
        elif check_flag == 1:
            if read_list[i] == 94 :
                check_flag = 2
            real_read_packet.append(read_list[i])
        elif check_flag == 2 :
            if read_list[i] == 94:
                check_flag= 3
            else :
                read_len_str+=chr(read_list[i])
            real_read_packet.append(read_list[i])
        elif check_flag == 3:
            if read_len == -2 :
                read_len = int(read_len_str)
            read_len = read_len-1
            real_read_packet.append(read_list[i])
            if read_len == -1:
                break
    
    if read_len == -1:
        read_hex = ""
        for i in real_read_packet:
            read_hex +=hex(i)+" "
        read_label_set(read_hex)
        ble_read_init()

# def ble_read(read):
#     global read_characteristic, check_flag, real_read_packet,read_len_str, read_len
#     print("[BLE] Read ! : ", read)
    
#     read_list = list(read)
#     for i in range(len(read_list)):
#         if read_list[i] == 2 and (read_list[i+1] == 56 or read_list[i+1] == 57) :
#             check_flag = 1
#             real_read_packet.append(read_list[i])
#         elif check_flag == 1:
#             if read_list[i] == 94 :
#                 check_flag = 2
#             real_read_packet.append(read_list[i])
#         elif check_flag == 2 :
#             if read_list[i] == 94:
#                 check_flag= 3
#             else :
#                 read_len_str+=chr(read_list[i])
#             real_read_packet.append(read_list[i])
#         elif check_flag == 3:
#             if read_len == -2 :
#                 read_len = int(read_len_str)
#             read_len = read_len-1
#             real_read_packet.append(read_list[i])
#             if read_len == -1:
#                 break
    
#     if read_len == -1:
#         read_hex = ""
#         for i in real_read_packet:
#             read_hex +=hex(i)+" "
#         read_label_set(read_hex)
#         print(read_hex)
#         ble_read_init()

async def ble_write(data):
    global write_characteristic, ble_client
    print("[BLE] Write ! :", data)
    write_hex = ""
    if len(data)>=17:
        write_hex = data[0:16]
        await ble_client.write_gatt_char(write_characteristic, data[0:16])
        await ble_write(data[16:len(data)])
    else:
        write_hex = data
        await ble_client.write_gatt_char(write_characteristic, data)
    write_label_set(write_hex)

"""
ble connection function
"""

def ble_init():
    global ble_client, ble_connect, ble_program_type
    ble_client = None
    ble_connect=False
    ble_program_type=-1

def on_disconnect(client):
    print("[BLE CALLBACK] Client with address {} got disconnected!".format(client.address))
    ble_init()
    ui_update()
    

async def run(address): 
    global write_characteristic, ble_client, ble_connect, read_characteristic, select_address
    status_label_set("STATUS : Connecting.. ")
    client = BleakClient(address)
    try:
        # 장치 연결 해제 콜백 함수 등록
        client.set_disconnected_callback(on_disconnect)
         # 장치 연결 시작
        await client.connect()
        status_label_set("STATUS : Connect "+address)
        ble_client = client
        ble_connect = True
        ui_update()
        print("[BLE] Connect!")
        services = await client.get_services() 
        for service in services:
            for characteristic in service.characteristics:
                if characteristic.uuid == read_write_charcteristic_uuid:                       
                    if 'write' in characteristic.properties:
                        write_characteristic = characteristic
                        read_characteristic = characteristic

        if client.is_connected:
            while(ble_connect):
                await ble_read()
                await asyncio.sleep(1)
    except Exception as e:
        # 연결 실패시 발생
        print('[ERR] : ', e) 
    finally:
        # 장치 연결 해제
        await client.disconnect()    
    print("[BLE] Disconnect")
    scan_init()
    status_label_set("STATUS : Disconnect ")

"""
scan function
"""
def scan_init():
    global devicelistbox, devicelistnum, devicelist, select_address
    devicelistnum = 0
    devicelist = []
    devicelistbox.delete(0, END)
    select_address = None

def detection_callback(device, advertisement_data):
    # 장치 주소와 신호세기, 그리고 어드버타이징 데이터를 출력한다.
    global devicelistbox, devicelistnum, devicelist
    if device.name is not None:
        device_info = f'{device.name} {device.address}'
        if device_info not in devicelist:
            devicelist.append(device_info)
            devicelistbox.insert(devicelistnum, device_info)

async def scan(): 
    global scanner, scanning
    scan_init()
    # 검색 클래스 생성
    scanner = BleakScanner()
    # 콜백 함수 등록
    scanner.register_detection_callback(detection_callback)

    # 검색 시작
    await scanner.start()
    print("[BLE] SCAN START")
    status_label_set("STATUS : Scanning")
    # 5초간 대기 이때 검색된 장치들이 있다면 등록된 콜백함수가 호출된다.
    scanning = True

    while(scanning):
        await asyncio.sleep(1)
    await scanner.stop()    
    print("[BLE] SCAN STOP")
    
    status_label_set("STATUS : Scan Stop")

async def scan_stop():
    global scanning
    scanning = False

"""
asyncio loop function
"""

def asyncio_ble_connect_thread(loop):
    global devicelistbox, select_address
    select_address = None
    for i in devicelistbox.curselection():
        select_address = devicelistbox.get(i).split(' ')[1]
        break
    if select_address:
        loop.create_task(scan_stop())
    else:
        print("Please select ble device !")

def asyncio_ble_connect_stop(loop):
    loop.create_task()

def asyncio_thread(loop):
    global select_address
    loop.run_until_complete(scan())
    if select_address :

        loop.run_until_complete(run(select_address))

def asyncio_ble_write_thread(loop, protocol):
    loop.create_task(ble_write(protocol))

def asyncio_scan_stop_thread(loop):
    loop.create_task(scan_stop())


"""
task function
"""
def do_ble_connect_tasks(loop):
    threading.Thread(target=asyncio_ble_connect_thread, args=(loop,)).start()

def do_scan_tasks(loop,root):
    print("[BTN EVENT] SCAN START")
    threading.Thread(target=asyncio_thread, args=(loop,)).start()

def do_scan_stop_tasks(loop):
    print("[BTN EVENT] SCAN STOP")
    threading.Thread(target=asyncio_scan_stop_thread, args=(loop,)).start()

def do_ble_write_tasks(loop, protocol):
    threading.Thread(target=asyncio_ble_write_thread, args=(loop,protocol,)).start()

"""
ui update
"""
def ui_update():
    global ble_connect
    global root, text, devicelistbox, read_text, write_text,status_text,scan_btn, connect_btn,frame,scrollbar,scan_stop_btn
    global close_btn, measure_btn, stop_btn, get_hr_btn, get_spo2_btn, random_btn, write_label, read_label, label, submit_btn
    if ble_connect: #연결돼있으면
        scan_btn.grid_forget()
        scan_stop_btn.grid_forget()
        connect_btn.grid_forget()
        frame.grid_forget()
        scrollbar.pack_forget()
        devicelistbox.pack_forget() 

        close_btn.grid(row=1, column=0, sticky=W)
        measure_btn.grid(row=1,column=1,  sticky=W)
        stop_btn.grid(row=1, column=2, sticky=W)
        get_hr_btn.grid(row=2, column=0, sticky=W)
        get_spo2_btn.grid(row=2, column=1, sticky=W)
        random_btn.grid(row=2, column=2, sticky=W)
        write_label.grid(row=3, column=0, columnspan=3, sticky=W+E+N+S )
        read_label.grid(row=4, column=0, columnspan=3, sticky=W+E+N+S )
        text.grid(row=6, column=0, columnspan=3, sticky=W+E+N+S)
        submit_btn.grid(row=7, column=0, columnspan=3, sticky=W+E+N+S)
    else:
        scan_btn.grid(row=1, column=0, sticky=W)
        scan_stop_btn.grid(row=1, column=1, sticky=W)
        connect_btn.grid(row=1, column=2, sticky=W)
        frame.grid(row=2, column=0, columnspan=3, sticky=W+E+N+S )
        scrollbar.pack(side=RIGHT, fill=Y)
        devicelistbox.pack(expand=True, fill=Y)

        close_btn.grid_forget()
        measure_btn.grid_forget()
        stop_btn.grid_forget()
        get_hr_btn.grid_forget()
        get_spo2_btn.grid_forget()
        random_btn.grid_forget()
        write_label.grid_forget()
        read_label.grid_forget()
        label.grid_forget()
        text.grid_forget()
        submit_btn.grid_forget()

"""
button click function
"""
def measure_button(loop):
    print("[BTN EVENT] MEASURE START")
    global ble_program_type
    if ble_program_type == -1:
        ble_program_type = 1
        do_ble_write_tasks(loop, protocol.REQ_START_MEASURE)
        status_label_set("STATUS : REQUEST MEASURE START")

def get_command_button(loop, packet):
    global ble_program_type
    if ble_program_type == 1 :
        do_ble_write_tasks(loop, packet)
        status_label_set("STATUS : REQUEST GET CMD ")
    else :
        print("측정 버튼을 눌러주세요 !")  
         
def stop_button(loop):
    print("[BTN EVENT] MEASURE STOP")
    global ble_program_type
    if ble_program_type == 1 :
        ble_program_type = -1
        do_ble_write_tasks(loop, protocol.REQ_STOP_MEASURE)
        status_label_set("STATUS : REQUEST MEASURE STOP")

def disconnect_button():
    global ble_connect
    ble_connect = False
    print("[BTN EVENT] BLE Disconnect")
    
def randomdata():
    random_len = random.randrange(1, 17)
    packet = None
    packet_len = ""
    if random_len<10:
        packet_len = '0'+str(random_len)+'^'
    else : 
        packet_len = str(random_len)+'^'
    packet = bytearray([0x02, 0x31, 0x46, 0x5E])
    for p in bytearray(packet_len.encode()):
        packet.append(p)
    for d in range(random_len):
        packet.append(d+1)
    packet.append(0x03)
    return packet

def random_data_button(loop):
    status_label_set("STATUS : SEND READOME DATA")
    do_ble_write_tasks(loop,randomdata())

def submit_button(loop, packet_text):
    print("[BTN EVENT] INPUT Submit")
    packet = packet_text.get(1.0, END+"-1c")
        
    if len(packet) != 0:
        packet = packet.split(" ")
        submit_packet = []
        for i in packet:
            submit_packet.append(int(i, 16))
        do_ble_write_tasks(loop, bytearray(submit_packet))

def main(loop):
    global root, text, devicelistbox, read_text, write_text,status_text,scan_btn, connect_btn,frame,scrollbar,scan_stop_btn, ble_connect
    global close_btn, measure_btn, stop_btn, get_hr_btn, get_spo2_btn, random_btn, write_label, read_label, label, submit_btn
    
    root = Tk()
    root.title("GUI TEST")

    status_text = StringVar()
    status_text.set("STATUS : IDLE")

    status_label = Label(root, textvariable=status_text)
    status_label.grid(row=0, column=0, columnspan=3, sticky=W+E+N+S )
    scan_btn = Button(root, text="BLE Scan", command=lambda:do_scan_tasks(loop,root))
    scan_stop_btn = Button(root, text="BLE Scan Stop", command=lambda:do_scan_stop_tasks(loop))
    connect_btn = Button(root, text="BLE Connect", command=lambda:do_ble_connect_tasks(loop))
    frame = Frame(root)
    scrollbar = Scrollbar(frame, orient="vertical")
    devicelistbox = Listbox(frame, selectmode='extended', yscrollcommand=scrollbar.set, height=0)
    # -----------------------------------------------------------------------------------------
    close_btn = Button(root, text="BLE Disconnect", command=disconnect_button)

    measure_btn = Button(root, text="Measure Start", command=lambda:measure_button(loop))
    stop_btn = Button(root, text="Measure Stop", command=lambda:stop_button(loop))
    get_hr_btn = Button(root, text="GET HR", command=lambda:get_command_button(loop, protocol.REQ_GET_HR))
    get_spo2_btn = Button(root, text="GET SPO2", command=lambda:get_command_button(loop, protocol.REQ_GET_SPO2))

    random_btn = Button(root, text="Random Data", command=lambda:random_data_button(loop))
    
    read_text = StringVar()
    read_text.set("READ DATA : ")

    write_text = StringVar()
    write_text.set("READ DATA : ")   

    write_label=Label(root, textvariable=write_text)
    read_label=Label(root, textvariable=read_text)
    
    label=Label(root, text="Packet Input ex) 02 30 36 5E 30 31 5E 01 03")
    label.grid(row=5, column=0, columnspan=3, sticky=W+E+N+S)
    
    text=Text(root)
    submit_btn = Button(root, text="Submit", command=lambda:submit_button(loop,text))
    ble_init()
    ui_update()

    root.mainloop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)