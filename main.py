import asyncio
from bleak import BleakClient, BleakScanner
from tkinter import *
from datetime import datetime
import threading
import random
address = "F4:60:77:FF:23:F0"
read_write_charcteristic_uuid = "f0001111-0451-4000-b000-000000000000"

write_characteristic = None
read_characteristic = None
ble_client = None
ble_close = True
ble_program_type = -1
ble_run_state = False
root = None
text = None
submit_packet = []
devicelistbox = None
devicelistnum = 0
devicelist = []
scanner = None
scanning = True
select_address = None
read_text = None
write_text = None
status_text = None
scan_btn = None
packet_write = False
real_read_packet = []
check_flag = 0
read_len_str = ""
read_len = -2
packet_loss=0
async def ble_write(data):
    global write_characteristic, ble_client, write_text, packet_write
    print("BLE Write ! :", data)
    write_hex = ""
    if len(data)>=17:
        await ble_client.write_gatt_char(write_characteristic, data[0:16])
        
        for i in list(data[0:16]) :
            write_hex += hex(i)+" "
       
        await ble_write(data[16:len(data)])
    else:
        await ble_client.write_gatt_char(write_characteristic, data)
        for i in list(data) :
            write_hex += hex(i)+" "
        write_text.set("WRITE DATA : "+write_hex+"\n")
    packet_write = True

async def ble_read():
    global read_characteristic, read_text, check_flag, packet_write,real_read_packet,read_len_str, read_len,packet_loss
    read = await ble_client.read_gatt_char(read_characteristic)
    print("BLE Read ! : ", read)
    read_hex = ""
    read_list = list(read)
    for i in range(len(read_list)):
        if check_flag == 1 :
            if read_list[i] == 94 :
                check_flag = 2
            real_read_packet.append(read_list[i])
        elif check_flag == 2:
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
                check_flag = 0
                read_len_str = ""
                read_len = -2
                packet_write = False
                break
        else:
            if read_list[i] == 2 and read_list[i+1] == 56 :
                check_flag = 1
                real_read_packet.append(read_list[i])
    
    if packet_write == False:
        for i in real_read_packet:
            read_hex +=hex(i)+" "
        real_read_packet = []
        print(read_hex)
        read_text.set("READ DATA : "+read_hex+"\n")
        read_hex = ""
    else:
        if packet_loss == 3:
            print("Packet Loss 발생 ! 다시 데이터를 요청하세요 !")
            check_flag = 0
            read_len_str = ""
            read_len = -2
            real_read_packet = []
            packet_write = False
    packet_loss+=1
async def get_hr():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x39, 0x5E, 0x30, 0x31, 0x5E, 0x01, 0x03]))

async def get_spo2():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x38, 0x5E, 0x30, 0x31, 0x5E, 0x01, 0x03]))

async def start_measure():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x36, 0x5E, 0x30, 0x31, 0x5E, 0x01, 0x03]))

async def stop():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x37, 0x5E, 0x30, 0x31, 0x5E, 0x01, 0x03]))   

async def randomdata():
    global ble_run_state, status_text
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
    status_text.set("STATUS : SEND READOME DATA")
    await ble_write(packet)

def measure_button():
    print("measure button click!")
    global ble_program_type, ble_run_state, status_text
    ble_program_type = 1
    ble_run_state = False
    status_text.set("STATUS : REQUEST MEASURE START")

def get_hr_button():
    print("get hr button click!")
    global ble_program_type, ble_run_state, status_text
    if ble_program_type == 1 or ble_program_type == 2 :
        ble_program_type = 2
        ble_run_state = False
        status_text.set("STATUS : REQUEST GET HR ")
    else :
        print("측정 버튼을 눌러주세요 !")

def stop_button():
    print("stop button click!")
    global ble_program_type, ble_run_state, status_text
    ble_program_type = 3
    ble_run_state = False
    status_text.set("STATUS : REQUEST MEASURE STOP")

def disconnect_button():
    global ble_client, root
    print("disconnect button click!")
    # if ble_client==None:
    #     root.destroy()
    global ble_close
    ble_close = False
    
def random_data_button():
    global ble_run_state, ble_program_type
    ble_program_type = 0
    ble_run_state = False  

def submit_button():
    print("submit button click !")
    global text, submit_packet, ble_run_state, ble_program_type
    ble_program_type = 4
    packet = text.get(1.0, END+"-1c")
        
    if len(packet) != 0:
        packet = packet.split(" ")
        submit_packet = []
        for i in packet:
            submit_packet.append(int(i, 16))
        submit_packet = bytearray(submit_packet)
    ble_run_state = False

def detection_callback(device, advertisement_data):
    # 장치 주소와 신호세기, 그리고 어드버타이징 데이터를 출력한다.
    global devicelistbox, devicelistnum, devicelist
    if device.name is not None:
        device_info = f'{device.name} {device.address}'
        if device_info not in devicelist:
            devicelist.append(device_info)
            devicelistbox.insert(devicelistnum, device_info)

def on_disconnect(client):
    global ble_close
    ble_close=False
    print("Client with address {} got disconnected!".format(client.address))

async def run(address): 
    global write_characteristic, ble_client, ble_close, ble_program_type, read_characteristic, ble_run_state, submit_packet, status_text,scan_btn, packet_write 
    status_text.set("STATUS : Connecting.. ")
    client = BleakClient(address)
    try:
        # 장치 연결 해제 콜백 함수 등록
        client.set_disconnected_callback(on_disconnect)
         # 장치 연결 시작
        await client.connect()
        scan_btn.pack_forget()
        status_text.set("STATUS : Connect "+address)
        ble_client = client
        ble_close=True
        ble_program_type=-1
        ble_run_state = True

        print("connect!")
        services = await client.get_services() 
        for service in services:
            for characteristic in service.characteristics:
                if characteristic.uuid == read_write_charcteristic_uuid:                       
                    if 'write' in characteristic.properties:
                        write_characteristic = characteristic
                        read_characteristic = characteristic
        if client.is_connected:
            while(ble_close):
                if ble_program_type == 0:
                    await randomdata()
                elif ble_program_type==1:
                    if ble_run_state == False: 
                        await start_measure()
                elif ble_program_type==2:
                    if ble_run_state == False: 
                        await get_hr()
                elif ble_program_type==3:
                    if ble_run_state == False: 
                        await stop()
                elif ble_program_type==4:
                    if ble_run_state == False: 
                        await ble_write(submit_packet)
                ble_run_state = True
                if packet_write:
                    await ble_read()
                await asyncio.sleep(1)
        else:
            print(client)
    except Exception as e:
        # 연결 실패시 발생
        print('error: ', e, end='')     
    finally:
        print('start disconnect')
        # 장치 연결 해제
        await client.disconnect()
    status_text.set("STATUS : Disconnect ")

def selected_item(loop):
    threading.Thread(target=asyncio_connect_thread, args=(loop,)).start()

async def scan(address, root, loop): 
    global scanner, scanning, devicelistbox, devicelistnum, devicelist,status_text
    
    devicelistnum = 0
    devicelist = []
    devicelistbox.delete(0, END)
    # 검색 클래스 생성
    scanner = BleakScanner()
    # 콜백 함수 등록
    scanner.register_detection_callback(detection_callback)

    # 검색 시작
    await scanner.start()
    print("scan start!")
    status_text.set("STATUS : Scanning")
    # 5초간 대기 이때 검색된 장치들이 있다면 등록된 콜백함수가 호출된다.
    scanning = True
    while(scanning):
        await asyncio.sleep(1)
    print("scan stop")
    status_text.set("STATUS : Scan Stop")

async def scan_stop():
    global scanner, scanning
    scanning = False
    print("scan stop click!")
    await asyncio.sleep(1)
    await scanner.stop()

def asyncio_connect_thread(loop):
    global devicelistbox, select_address
    select_address = None
    for i in devicelistbox.curselection():
        select_address = devicelistbox.get(i).split(' ')[1]
        break
    if select_address:
        loop.create_task(scan_stop())

    else:
        print("Please select ble device !")

def asyncio_thread(loop, root):
    global address, select_address
    loop.run_until_complete(scan(address, root, loop))
    if select_address :
        loop.run_until_complete(run(select_address))

def asyncio_scan_stop_thread(loop):
    loop.create_task(scan_stop())

def do_scan_tasks(loop,root):
    threading.Thread(target=asyncio_thread, args=(loop,root,)).start()

def do_scan_stop_tasks(loop):
    threading.Thread(target=asyncio_scan_stop_thread, args=(loop,)).start()

def main(loop):
    global root, text, devicelistbox, read_text, write_text,status_text,scan_btn
    root = Tk()
    root.title("GUI TEST")
    status_text = StringVar()
    status_text.set("STATUS : IDLE")
    status_label = Label(root, textvariable=status_text)
    status_label.grid(rowspan=1)
    scan_btn = Button(root, text="BLE Scan", command=lambda:do_scan_tasks(loop,root))
    scan_btn.grid(row=1, column=0, sticky=W)
    scan_stop_btn = Button(root, text="BLE Scan Stop", command=lambda:do_scan_stop_tasks(loop))
    scan_stop_btn.grid(row=2, column=0, sticky=W)

    connect_btn = Button(root, text="BLE Connect", command=lambda:selected_item(loop))
    connect_btn.grid(row=1, column=1, sticky=W)

    close_btn = Button(root, text="BLE Disconnect", command=disconnect_button)
    close_btn.grid(row=2, column=1, sticky=W)

    frame = Frame(root)
    frame.grid(row=3, column=0, sticky=N+S)

    root.rowconfigure(3, weight=1)
    root.columnconfigure(3, weight=1)
    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)
    devicelistbox = Listbox(frame, selectmode='extended', yscrollcommand=scrollbar.set, height=0)
    devicelistbox.pack(expand=True, fill=Y)

    measure_btn = Button(root, text="Measure Start", command=measure_button)
    measure_btn.grid(column=3, row=1)

    stop_btn = Button(root, text="Measure Stop", command=stop_button)
    stop_btn.grid(column=4, row=1)

    get_hr_btn = Button(root, text="GET HR", command=get_hr_button)
    get_hr_btn.grid(column=3, row=2)

    random_btn = Button(root, text="Random Data", command=random_data_button)
    random_btn.grid(column=4, row=2)

    label=Label(root, text="Packet Input ex) 02 30 36 5E 30 31 5E 01 03")
    label.grid(columnspan=1)
    
    text=Text(root, height=10, width=30)
    text.grid(column=0, row=6)
    submit_btn = Button(root, text="Submit", command=submit_button)
    submit_btn.grid(column=1, row=6)
    read_text = StringVar()
    read_text.set("READ DATA")
    write_text = StringVar()
    write_text.set("WRITE DATA")
    write_label=Label(root, textvariable=write_text)
    write_label.grid(column=1, row=3)
    read_label=Label(root, textvariable=read_text)
    read_label.grid(column=1, row=4)
    

    root.mainloop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)