import asyncio
from bleak import BleakClient
from tkinter import *
from datetime import datetime
import threading

address = "F4:60:77:FF:23:F0"
read_write_charcteristic_uuid = "foo01111-0451-4000-booo-oooooo000000"

write_characteristic = None
read_characteristic = None
ble_client = None
ble_close = True
ble_program_type = 0
ble_run_state = False
root = None

async def ble_write(data):
    global write_characteristic, ble_client
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
    global ble_run_state 
    ble_run_state = False
    await asyncio.sleep(0.3)
    await ble_write(bytearray([0x02, 0x30, 0x39, 0x03]))

async def start_measure():
    global ble_run_state
    ble_run_state = False
    await asyncio.sleep(0.3)
    await ble_write(bytearray[0x02, 0x30, 0x36, 0x03])

async def stop():
    global ble_run_state 
    ble_run_state = False
    await ble_write(bytearray([0x02, 0x30, 0x37, 0x30]))  

def measure_button():
    print("measure button click!")
    global ble_program_type, ble_run_state
    ble_program_type = 1
    ble_run_state = False

def get_hr_button():
    print("get hr button click!")
    global ble_program_type, ble_run_state
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
    
    
async def run(address, root, loop):    
    async with BleakClient(address, timeout=5.0) as client:
        global write_characteristic, ble_client, ble_close, ble_program_type, read_characteristic
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
                if ble_program_type==1:
                    if ble_run_state == False: 
                        await start_measure()
                elif ble_program_type==2:
                    if ble_run_state == False: 
                        await get_hr()
                elif ble_program_type==3:
                    if ble_run_state == False: 
                        await stop()
                ble_run_state = True
                await asyncio.sleep(3)
    print('disconnect')
    loop.close()
    root.destroy()
def asyncio_thread(loop, root):
    global address
    loop.run_until_complete(run(address, root, loop))
    

def do_tasks(loop,root):
    threading.Thread(target=asyncio_thread, args=(loop,root,)).start()

def main(loop):
    global root 
    root = Tk()
    root.title("GUI TEST")
    root.geometry('500x200')
    connect_btn = Button(root, text="BLE Connect", command=lambda:do_tasks(loop,root))
    connect_btn.pack()

    measure_btn = Button(root, text="START MEASURE", command=measure_button)
    measure_btn.pack()

    get_hr_btn = Button(root, text="GET HR", command=get_hr_button)
    get_hr_btn.pack()

    stop_btn = Button(root, text="STOP MEASUREMENT", command=stop_button)
    stop_btn.pack()

    close_btn = Button(root, text="CLOSE", command=close_button)
    close_btn.pack()

    root.mainloop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)

