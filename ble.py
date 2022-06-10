import asyncio
from bleak import BleakClient, BleakScanner
import protocol
import threading, time, copy
read_write_charcteristic_uuid = "f0001111-0451-4000-b000-000000000000"
class BLE:
    def __init__(self):
        self.loop = None

        self.scanner = None
        self.is_scanning = False

        self.devicelist = None
        self.select_address = None
        
        self.root = None
        self.connected_client = []

        self.is_running = False

    def root_connect(self, root):
        self.root = root

    def scan_init(self):
        self.root.devicelistbox_init()
        self.devicelist = []
        self.select_address = None

    def do_asyncio_tasks(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.asyncio_thread).start()
    def do_asyncio_stop_tasks(self):
        threading.Thread(target=self.asyncio_stop_thread, args=(False,)).start()
    def do_asyncio_close_tasks(self):
        return threading.Thread(target=self.asyncio_stop_thread, args=(True,))
    def do_scan_tasks(self):
        print("[BTN EVENT] SCAN START")
        threading.Thread(target=self.asyncio_scan_thread).start()
    def do_scan_stop_tasks(self):
        print("[BTN EVENT] SCAN STOP")
        threading.Thread(target=self.asyncio_scan_stop_thread).start()
    def do_ble_connect_tasks(self):
        print("[BTN EVENT] BLE CONNECT")
        threading.Thread(target=self.asyncio_ble_connect_thread).start()
    
    def do_ble_disconnect_tasks(self):
        print("[BTN EVENT] BLE DISCONNECT")
        threading.Thread(target=self.asyncio_ble_disconnect_thread).start()
    
    def do_ble_write_tasks(self, packet):
        threading.Thread(target=self.asyncio_ble_write_thread, args=(packet,)).start()

    def asyncio_thread(self):
        self.loop.run_until_complete(self.asyncio_start())
        self.loop.close()
        if not self.root.get_close_status() :
            self.root.change_ui(self.is_running)

    def asyncio_stop_thread(self, is_close):
        if self.is_running:
            self.loop.create_task(self.asyncio_stop(is_close))
        else :
            print("비동기 루프 실행 상태가 아닙니다.")

    def asyncio_scan_thread(self):
        self.loop.create_task(self.ble_scan())

    def asyncio_scan_stop_thread(self):
        self.loop.create_task(self.ble_scan_stop())

    def asyncio_ble_connect_thread(self):
        address = self.root.devicelistbox_return()
        if self.is_click_device(address) :
            self.loop.create_task(self.ble_connect(address))
        
    def asyncio_ble_disconnect_thread(self):
        address = self.root.clientlistbox_return()
        if self.is_click_device(address):
            self.loop.create_task(self.ble_disconnect(address))   

    def asyncio_ble_write_thread(self, packet):
        address = self.root.clientlistbox_return()
        if self.is_click_device(address):
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                print("ble_write_check")
                self.loop.create_task(self.ble_write_check(index, packet))

    def is_click_device(self, address):
        if address:
            return True
        else:
            print("Please select ble device !")
            return False
    def get_index_select_client(self, address):
        for i in range(len(self.connected_client)):
            if self.connected_client[i].address == address:
                return i
        print("Disconnected Device !")
        return None
    def detection_callback(self, device, advertisement_data):
        if device.name is not None:
            device_info = f'{device.name} {device.address}'
            if device_info not in self.devicelist:
                self.devicelist.append(device_info)
                self.root.devicelist_insert(len(self.devicelist)-1, device_info)

    def get_is_running(self):
        return self.is_running

    async def asyncio_start(self):
        if not self.is_running: 
            self.is_running = True
            self.root.change_ui(self.is_running)
            while self.is_running:
                await asyncio.sleep(1)
        else :
            print("비동기 루프를 실행중입니다.")

    async def asyncio_stop(self, is_close):
        await self.ble_scan_stop(is_close)
        await self.ble_all_disconnect(is_close)
        await asyncio.sleep(2)
        self.is_running = False


    async def ble_scan(self):
        if not self.is_scanning : 
            self.scan_init()
            self.scanner = BleakScanner()
            self.scanner.register_detection_callback(self.detection_callback)
            await self.scanner.start()
            self.root.status_label_set("STATUS : Scanning..")
            self.is_scanning = True
        else :
            print("스캔 상태 입니다.")

    async def ble_scan_stop(self, is_close):
        if self.is_scanning:
            await self.scanner.stop()  
            self.is_scanning = False  
            if not is_close:
                self.root.status_label_set("STATUS : Scan Stop")
        else :
            print("스캔 종료 상태 입니다.")
    def on_disconnect(self, client):
        print("[BLE CALLBACK] Client with address {} got disconnected!".format(client.address))
        self.root.clientlistbox_find_delete(client.address)
        for i in range(len(self.connected_client)) :
            if self.connected_client[i].address == client.address:
                del self.connected_client[i]
                break

    async def ble_connect(self, address):
        self.root.status_label_set("STATUS : Connecting..")
        self.connected_client.append(BleakClient(address.split(' ')[1]))
        client = self.connected_client[len(self.connected_client)-1]
        try:
            client.set_disconnected_callback(self.on_disconnect)
            await client.connect()
            self.root.clientlistbox_insert(len(self.connected_client)-1, address)
            self.root.status_label_set(f"STATUS : Connected "+client.address)
        except Exception as e:
            print('[ERR] : ', e) 
        finally:
            await asyncio.sleep(1) 

    async def ble_disconnect(self, address):
        for i in range(len(self.connected_client)) :
            if self.connected_client[i].address == address.split(' ')[1]:
                
                await asyncio.sleep(1)
                await self.connected_client[i].disconnect()
                break
    async def ble_all_disconnect(self):
        temp_list = self.connected_client.copy()
        for i in range(len(temp_list)) :
            await asyncio.sleep(1)
            await temp_list[i].disconnect()
            
    async def ble_write_check(self, index, data):
        if len(data)>=17:
            await self.ble_write(index, data[0:16])
            await self.ble_write_check(data[16:len(data)])
        else:
            await self.ble_write(index, data[0:16])
        
    async def ble_write(self, i, data):
        self.root.write_label_set(data)
        await asyncio.sleep(1)
        print("[BLE] WRITE ", data)
        await self.connected_client[i].write_gatt_char(read_write_charcteristic_uuid,  data)
        
    
    