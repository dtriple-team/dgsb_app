import asyncio
from bleak import BleakClient, BleakScanner
import protocol
import threading, time
class BLE:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.scanner = None
        self.is_scanning = None

        self.devicelist = None
        self.select_address = None
        
        self.root = None
        self.connected_client = []

        self.running = True
    def root_connect(self, root):
        self.root = root

    def scan_init(self):
        self.root.devicelistbox_init()
        self.devicelist = []
        self.select_address = None

    def do_scan_tasks(self):
        print("[BTN EVENT] SCAN START")
        threading.Thread(target=self.asyncio_scan_thread).start()

    def do_ble_connect_tasks(self):
        print("[BTN EVENT] BLE CONNECT")
        threading.Thread(target=self.asyncio_ble_connect_thread).start()

    def asyncio_scan_thread(self):
        self.loop.run_until_complete(self.ble_scan())
        # if self.select_address:
        #     self.loop.run_until_complete(self.ble_connect())

    def asyncio_ble_connect_thread(self):
        self.select_address = self.root.devicelistbox_return()
        print()
        if self.select_address :
            self.ble_scan_stop()
        else :
            print("Please select ble device !")
        self.loop.create_task(self.ble_connect(self.select_address))
           
    def detection_callback(self, device, advertisement_data):
        if device.name is not None:
            device_info = f'{device.name} {device.address}'
            if device_info not in self.devicelist:
                self.devicelist.append(device_info)
                self.root.devicelist_insert(len(self.devicelist)-1, device_info)

    async def ble_scan(self):
        self.scan_init()
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)
        await self.scanner.start()
        self.root.status_label_set("STATUS : Scanning..")
        self.scanning = True
        while(self.scanning):
            await asyncio.sleep(1)
        await self.scanner.stop()    
        self.root.status_label_set("STATUS : Scan Stop")
        while self.running:
            await asyncio.sleep(1)
    def ble_scan_stop(self):
        print("[BTN EVENT] SCAN STOP")
        self.scanning = False

    def on_disconnect(self, client):
        print("[BLE CALLBACK] Client with address {} got disconnected!".format(client.address))
        self.root.status_label_set(f"STATUS : Disonnected "+client.address)
        for i in range(len(self.connected_client)) :
            if self.connected_client[i].address == client.address:
                del self.connected_client[i]
                break

    async def ble_connect(self, address):
        self.root.status_label_set("STATUS : Connecting..")
        print(address)
        self.connected_client.append(BleakClient(address))
        client = self.connected_client[len(self.connected_client)-1]
        try:
            client.set_disconnected_callback(self.on_disconnect)
           
            await client.connect()
            self.root.status_label_set(f"STATUS : Connected "+client.address)
        except Exception as e:
            print('[ERR] : ', e) 
        finally:
            await asyncio.sleep(1) 
        print("[BLE] Disconnect")

