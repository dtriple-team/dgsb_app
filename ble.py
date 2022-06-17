import asyncio, threading, file, protocol
from bleak import BleakClient, BleakScanner
from ble_print import print_hex
file_test = False
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
        self.vital_loop = []
        self.random_loop = []
        if file_test:
            self.file_write_ble = file.File()
            self.file_write_ble.file_write_init("ble.txt")
        
    def root_connect(self, root):
        self.root = root

    def scan_init(self):
        self.root.scanlistbox_init()
        self.devicelist = []
        self.select_address = None
        
    def is_click_device(self, address):
        if address:
            return True
        else:
            print("[NOTIFICATION] Please select ble device !")
            return False

    def get_index_select_client(self, address):
        for i in range(len(self.connected_client)):
            if self.connected_client[i].address == address:
                return i
        print("[NOTIFICATION] Disconnected Device !")
        return -1

    def get_is_running(self):
        return self.is_running
    """
    callback function
    """  
    def scan_detection_callback(self, device, advertisement_data):
        if device.name is not None and "DGSB" in device.name:
            device_info = f'{device.name} {device.address}'
            if device_info not in self.devicelist:
                self.devicelist.append(device_info)
                self.root.devicelist_insert(len(self.devicelist)-1, device_info)
                
    def ble_disconnect_callback(self, client):
        print("[BLE CALLBACK] Client with address {} got disconnected!".format(client.address))
        self.root.status_label_set(f'Disconnect ! {client.address}')
        self.root.clientlistbox_find_delete(client.address)
        if client.address in self.vital_loop:
            self.vital_loop.remove(client.address)
        if client in self.connected_client:
            self.connected_client.remove(client)

    """
    thread task function
    """  
    def do_asyncio_tasks(self):
        print("[BTN EVENT] PROGRAM START")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.asyncio_thread).start()

    def do_asyncio_stop_tasks(self):
        print("[BTN EVENT] PROGRAM STOP")
        threading.Thread(target=self.asyncio_stop_thread).start()

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
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_thread, args=(packet,)).start()

    def do_ble_write_loop_tasks(self, packet):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_loop_thread, args=(packet,)).start()
    def do_ble_write_random_loop_tasks(self):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_random_loop_thread).start()
    """
    asyncio thread function
    """  
    def asyncio_thread(self):
        self.loop.run_until_complete(self.asyncio_start())
        self.loop.close()
        if file_test :
            self.file_write_ble.file_write_close()
        self.root.change_ui(self.is_running)

    def asyncio_stop_thread(self):
        if self.is_running:
            self.loop.create_task(self.asyncio_stop())
        else :
            print("[NOTIFICATION] It is not currently asynchronous.")

    def asyncio_scan_thread(self):
        self.loop.create_task(self.ble_scan())

    def asyncio_scan_stop_thread(self):
        self.loop.create_task(self.ble_scan_stop())

    def asyncio_ble_connect_thread(self):
        address = self.root.scanlistbox_return()
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
                if self.connected_client[index].address in self.vital_loop:
                    self.vital_loop.remove(self.connected_client[index].address)
                self.loop.create_task(self.ble_write_check(self.connected_client[index], packet))

    def asyncio_ble_write_loop_thread(self, packet):
        address = self.root.clientlistbox_return()
        if self.is_click_device(address):
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                if self.connected_client[index].address in self.vital_loop:
                    self.vital_loop.remove(self.connected_client[index].address)
                else:
                    self.vital_loop.append(self.connected_client[index].address)
                    self.loop.create_task(self.ble_write_loop(self.connected_client[index], packet))
    def asyncio_ble_write_random_loop_thread(self):
        address = self.root.clientlistbox_return()
        if self.is_click_device(address):
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                if self.connected_client[index].address in self.random_loop:
                    self.random_loop.remove(self.connected_client[index].address)
                else:
                    self.random_loop.append(self.connected_client[index].address)
                    self.loop.create_task(self.ble_write_random_loop(self.connected_client[index]))
    async def asyncio_start(self):
        if not self.is_running: 
            self.is_running = True
            self.root.change_ui(self.is_running)
            while self.is_running:
                await asyncio.sleep(1)
        else :
            print("[NOTIFICATION] It is currently asynchronous.")

    async def asyncio_stop(self):
        await self.ble_scan_stop()
        await self.ble_all_disconnect()
        await asyncio.sleep(2)
        self.is_running = False

    """
    ble function
    """  
    async def ble_scan(self):
        if not self.is_scanning : 
            self.scan_init()
            self.scanner = BleakScanner()
            self.scanner.register_detection_callback(self.scan_detection_callback)
            await self.scanner.start()
            self.root.scan_status_label_set("Scanning..")
            self.is_scanning = True
        else :
            print("[NOTIFICATION] It is currently in scan state.")

    async def ble_scan_stop(self):
        if self.is_scanning:
            await self.scanner.stop()  
            self.is_scanning = False  
            self.root.scan_status_label_set("Scan Stop")
        else :
            print("[NOTIFICATION] It is currently in scan stop state.")
    

    async def ble_connect(self, client_info):
        self.root.status_label_set(f"Connecting.. {client_info.split(' ')[1]}")
        self.connected_client.append(BleakClient(client_info.split(' ')[1]))
        client = self.connected_client[len(self.connected_client)-1]
        try:
            client.set_disconnected_callback(self.ble_disconnect_callback)
            await client.connect()
            self.root.clientlistbox_insert(len(self.connected_client)-1, client_info)
            self.root.status_label_set(f"Connected {client.address}")
            await asyncio.sleep(1) 
            await self.ble_read_thread(client)
                
        except Exception as e:
            print('[ERR] : ', e)
  
    async def ble_disconnect(self, address):
        for i in range(len(self.connected_client)) :
            if self.connected_client[i].address == address.split(' ')[1]:
                
                await asyncio.sleep(1)
                await self.connected_client[i].disconnect()
                break

    async def ble_all_disconnect(self):
        temp_list = self.connected_client.copy()
        for i in range(len(temp_list)) :
            self.vital_loop = []
            await asyncio.sleep(1)
            await temp_list[i].disconnect()
        
    async def ble_write(self, client, data):
        hex_data = print_hex(data)
        print(f"[BLE] WRITE {client.address} : {hex_data}")
        self.root.write_label_set(hex_data)
        if file_test:
            self.file_write_ble.file_write_time("WRITE", hex_data)
        await client.write_gatt_char(read_write_charcteristic_uuid,  data)

    async def ble_write_check(self, client, data):
        if len(data)>=17:
            await self.ble_write(client, data[0:16])
            await self.ble_write_check(data[16:len(data)])
        else:
            await self.ble_write(client, data[0:16])

    async def ble_write_loop(self, client, data):
        try:
            while  client.address in self.vital_loop:
                await self.ble_write_check(client, data)
                await asyncio.sleep(2)
        except:
            pass
    async def ble_write_random_loop(self, client):
        try:
            data = [protocol.REQ_GET_SPO2, protocol.REQ_GET_HR, protocol.REQ_GET_WALK, protocol.REQ_GET_RUN]
            i = 0
            while client.address in self.random_loop:
                if i>=len(data)-1: 
                    i=0
                await self.ble_write_check(client, data[i])
                await asyncio.sleep(2)
                i+=1
        except:
            pass

    async def ble_read(self, client):
        read_data = await client.read_gatt_char(read_write_charcteristic_uuid)
        hex_data = print_hex(read_data)
        if hex_data !="":
            print(f"[BLE] READ {client.address} : {hex_data}")
            if file_test:
                self.file_write_ble.file_write_time("READ",hex_data)
            self.root.read_label_set(hex_data)
        

    async def ble_read_thread(self, client):
        while client.is_connected:
            await self.ble_read(client)
            await asyncio.sleep(0.1)
    