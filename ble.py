import asyncio, threading, file, protocol
from bleak import BleakClient, BleakScanner
from ble_print import print_hex
file_test = True
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
        self.read_list = []
        if file_test:
            self.file_write_ble = file.File()
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
    def check_same_data(self, list, data):
        for l in list:
            if l.address == data:
                return True
        return False
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

    def do_ble_write_loop_tasks(self, packet, time):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_loop_thread, args=(packet,time,)).start()
    def do_ble_write_random_loop_tasks(self):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_random_loop_thread).start()
    """
    asyncio thread function
    """  
    def asyncio_thread(self):
        self.loop.run_until_complete(self.asyncio_start())
        self.loop.close()
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

    def asyncio_ble_write_loop_thread(self, packet, time):
        address = self.root.clientlistbox_return()
        if self.is_click_device(address):
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                if self.connected_client[index].address in self.vital_loop:
                    self.vital_loop.remove(self.connected_client[index].address)
                else:
                    self.vital_loop.append(self.connected_client[index].address)
                    self.loop.create_task(self.ble_write_loop(self.connected_client[index], packet, time))
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
        if not self.check_same_data(self.connected_client, client_info.split(' ')[1]):

            self.connected_client.append(BleakClient(client_info.split(' ')[1]))
            client = self.connected_client[len(self.connected_client)-1]
            try:
                client.set_disconnected_callback(self.ble_disconnect_callback)
                await client.connect()
                print("[BLE] Connect Success!")
                await asyncio.sleep(1)
                self.root.clientlistbox_insert(len(self.connected_client)-1, client_info)
                self.root.status_label_set(f"Connected {client.address}")
                await asyncio.sleep(1) 
                await self.ble_read_thread(client)
                    
            except Exception as e:
                print('[ERR] : ', e)
        else:
            print("[BLE] Already connected")
  
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
        if file_test:
            self.file_write_ble.file_write_time("WRITE", hex_data)
        await client.write_gatt_char(read_write_charcteristic_uuid,  data)

    async def ble_write_check(self, client, data):
        if len(data)>=21:
            await self.ble_write(client, data[0:20])
            await self.ble_write_check(data[20:len(data)])
        else:
            await self.ble_write(client, data)

    async def ble_write_loop(self, client, data, time):
        try:
            while  client.address in self.vital_loop:
                await self.ble_write_check(client, data)
                await asyncio.sleep(time)
        except:
            pass
    async def ble_write_random_loop(self, client):
        try:
            data = [protocol.REQ_GET_SPO2, protocol.REQ_GET_HR, protocol.REQ_GET_WALK_RUN, protocol.REQ_GET_MOTION_FLAG, protocol.REQ_GET_ACTIVITY, protocol.REQ_GET_BATT, protocol.REQ_GET_SCD, protocol.REQ_GET_ACC, protocol.REQ_GET_ALL_DATA]
            # data = [protocol.REQ_GET_SPO2, protocol.REQ_GET_HR]
            i = 0
            while client.address in self.random_loop:
                if i>=len(data): 
                    i=0
                await self.ble_write_check(client, data[i])
                await asyncio.sleep(0.3)
                i+=1
        except:
            pass

    async def ble_read(self, client):
        read_data = await client.read_gatt_char(read_write_charcteristic_uuid)
        if read_data != bytearray() :
            # self.ble_read_parsing(read_data)
            hex_data = print_hex(read_data)
            print(f"[BLE] READ {client.address} : {hex_data}")
            if file_test:
                self.file_write_ble.file_write_time("READ",hex_data)


    async def ble_read_thread(self, client):
        while client.is_connected:
            await self.ble_read(client)
            await asyncio.sleep(0.1)

    def ble_read_parsing(self, data):
        for i in list(data):
            if not self.read_list and i==2 :
                if i==2:
                    self.read_list.append(i)
                else :
                    print("[BLE READ] ERROR PACKET")
                    self.read_list = []
            else :
                self.read_list.append(i)
                if len(self.read_list)>=4 and len(self.read_list) == self.read_list[3]+6:
                    if i==3:
                        print(hex(self.read_list[1]), self.read_list[5:len(self.read_list)-1])
                        self.ble_read_classify_cmd(hex(self.read_list[1]), self.read_list[5:len(self.read_list)-1])
                        # print(f"[BLE READ] SUCCESS! CMD : {protocol.RESP_CMD[self.read_list[1]]} DATA : {self.read_list[5:len(self.read_list)-1]}")
                    else:
                        print("[BLE READ] ERROR PACKET")
                    self.read_list = []

    def ble_read_classify_cmd(self, cmd, data):
        if cmd == "0x83":
            spo2 = data[0]<<8 | data[1]
            spo2_confidence = data[2]
            print(f"spo2 = {spo2}, spo2_confidence = {spo2_confidence}")

        elif cmd == "0x84":
            hr = data[0]<<8 | data[1]
            hr_confidence = data[2]
            print(f"hr = {hr}, hr_confidence = {hr_confidence}")

        elif cmd == "0x85":
            walk = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
            run = data[4]<<24 | data[5]<<16 | data[6]<<8 | data[7]
            print(f"walk step = {walk}, run step = {run}")

        elif cmd == "0x86":
            motion_flag = data[0]<<8 | data[1]
            print(f"motion_flag = {motion_flag}")

        elif cmd == "0x87":
            print(f"activity = {data[0]}")

        elif cmd == "0x88":
            print(f"battery = {data[0]}")

        elif cmd == "0x89":
            scd = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
            print(f"scd = {scd}")

        elif cmd == "0x8a":
            acc_x = data[0]<<8 | data[1]
            acc_y = data[2]<<8 | data[3]
            acc_z = data[4]<<8 | data[5]
            print(f"acc_x = {acc_x}, acc_y = {acc_y}, acc_z = {acc_z}")

        elif cmd == "0x8b":
            gyro_x = data[0]<<8 | data[1]
            gyro_y = data[2]<<8 | data[3]
            gyro_z = data[4]<<8 | data[5]
            print(f"gyro_x = {gyro_x}, gyro_y = {gyro_y}, gyro_z = {gyro_z}")
        
        elif cmd == "0x8c":
            print(f"fall_detect = {data[0]}")
        
        elif cmd == "0x8d":
            temp = data[0]<<8 | data[1]
            print(f"temp = {temp}")
        
        elif cmd == "0x8e":
            pressure = data[0]<<8 | data[1]
            print(f"pressure = {pressure}")
        
        elif cmd == "0x8f":
            spo2 = data[0]<<8 | data[1]
            spo2_confidence = data[2]
            hr = data[3]<<8 | data[4]
            hr_confidence = data[5]
            walk = data[6]<<24 | data[7]<<16 | data[8]<<8 | data[9]
            run = data[10]<<24 | data[11]<<16 | data[12]<<8 | data[13]
            motion_flag = data[14]<<8 | data[15]
            activity = data[16]
            battery = data[17]
            scd = data[18]<<24 | data[19]<<16 | data[20]<<8 | data[21]
            acc_x = data[22]<<8 | data[23]
            acc_y = data[24]<<8 | data[25]
            acc_z = data[26]<<8 | data[27]
            gyro_x = data[28]<<8 | data[29]
            gyro_y = data[30]<<8 | data[31]
            gyro_z = data[32]<<8 | data[33]
            fall_detect = data[34]
            temp = data[35]
            pressure = data[36]<<8 | data[37]
            height = data[38]
            weight = data[39]
            age = data[40]
            gender = data[41]
            print(f"spo2 = {spo2}, spo2_confidence = {spo2_confidence} / hr = {hr}, hr_confidence = {hr_confidence} / walk step = {walk}, run step = {run} / motion_flag = {motion_flag} / activity = {activity} / battery = {battery} / scd = {scd} / acc_x = {acc_x}, acc_y = {acc_y}, acc_z = {acc_z} / gyro_x = {gyro_x}, gyro_y = {gyro_y}, gyro_z = {gyro_z} / fall_detect = {fall_detect} / temp = {temp} / pressure = {pressure} / height = {height}, weight = {weight}, age = {age}, gender = {gender}")
            
        elif cmd == "0x90":
            height = data[0]
            weight = data[1]
            age = data[2]
            gender = data[3]
            print(f"height = {height}, weight = {weight}, age = {age}, gender = {gender}")





