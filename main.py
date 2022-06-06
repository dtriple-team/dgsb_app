import asyncio
from bleak import BleakClient
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
async def ble_write(data):
    global write_characteristic, ble_client
    print("BLE Write ! :", data)
    if len(data)>=17:
        await ble_client.write_gatt_char(write_characteristic, data[0:16])
        await ble_write(data[16:len(data)])
    else:
        await ble_client.write_gatt_char(write_characteristic, data)
    
    await ble_read()

async def ble_read():
    global read_characteristic
    read = await ble_client.read_gatt_char(read_characteristic)
    print("read data : ", read)

async def get_hr():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x39, 0x03]))

async def start_measure():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x36, 0x03]))

async def stop():
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x37, 0x03]))  

async def randomdata():
    global ble_run_state
    random_len = random.randrange(0, 17)
    packet = None
    if random_len == 0 :
        packet = bytearray([0x02, 0x31, 0x46, 0x03])
    else:
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
    await ble_write(packet)


def measure_button():
    print("measure button click!")
    global ble_program_type, ble_run_state
    ble_program_type = 1
    ble_run_state = False

def get_hr_button():
    print("get hr button click!")
    global ble_program_type, ble_run_state
    if ble_program_type != 1 :
        print("측정 버튼을 눌러주세요 !")
    else :
        ble_program_type = 2
        ble_run_state = False

def stop_button():
    print("stop button click!")
    global ble_program_type, ble_run_state
    ble_program_type = 3
    ble_run_state = False

def close_button():
    global ble_client, root
    print("close button click!")
    if ble_client==None:
        root.destroy()
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
            submit_packet.append(int(i))
        submit_packet = bytearray(submit_packet)
    ble_run_state = False
    
async def run(address, root, loop):    
    async with BleakClient(address, timeout=5.0) as client:
        global write_characteristic, ble_client, ble_close, ble_program_type, read_characteristic, ble_run_state, submit_packet
        ble_client = client
        print('connected')
        services = await client.get_services()        
        for service in services:
            for characteristic in service.characteristics:
                if characteristic.uuid == read_write_charcteristic_uuid:                       
                    if 'write' in characteristic.properties:
                        write_characteristic = characteristic
                        read_characteristic = characteristic
        # client 가 연결된 상태라면  
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
                await asyncio.sleep(1)
    print('disconnect')
    loop.close()
    root.destroy()

def asyncio_thread(loop, root):
    global address
    loop.run_until_complete(run(address, root, loop))
    

def do_tasks(loop,root):
    threading.Thread(target=asyncio_thread, args=(loop,root,)).start()

def main(loop):
    global root, text
    root = Tk()
    root.title("GUI TEST")


    connect_btn = Button(root, text="BLE Connect", command=lambda:do_tasks(loop,root))
    connect_btn.grid(column=0, row=0)

    close_btn = Button(root, text="BLE Disconnect", command=close_button)
    close_btn.grid(column=1, row=0)

    measure_btn = Button(root, text="Measure Start", command=measure_button)
    measure_btn.grid(column=0, row=1)

    stop_btn = Button(root, text="Measure Stop", command=stop_button)
    stop_btn.grid(column=1, row=1)

    get_hr_btn = Button(root, text="GET HR", command=get_hr_button)
    get_hr_btn.grid(column=0, row=2)


    stop_btn = Button(root, text="Random Data", command=random_data_button)
    stop_btn.grid(column=1, row=2)

 
    label=Label(root, text="Packet Input ex) 02 30 39 03")
    label.grid(columnspan=2)
    
    text=Text(root, height=10, width=30)
    text.grid(column=0, row=4)
    submit_btn = Button(root, text="Submit", command=submit_button)
    submit_btn.grid(column=1, row=4)
    root.mainloop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
