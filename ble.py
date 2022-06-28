import asyncio, threading, file, protocol
from bleak import BleakClient, BleakScanner #BLE 통신을 위한 모듈
from ble_print import print_hex
from datetime import datetime
file_test = False # True-> write, read packet을 file로 확인할 수 있음
read_write_charcteristic_uuid = "f0001111-0451-4000-b000-000000000000"
class BLE:
    def __init__(self):
        self.loop = None # BLE와 통신하기 위한 Asynchronous loop 변수
        self.root = None # gui를 제어하기 위해 사용되는 root 변수
        self.is_running = False # 비동기 loop가 실행중인지 체크 

        #BLE scan에 사용되는 변수들
        self.scanner = None
        self.is_scanning = False
        self.scanlist = None
    
        self.connected_client_list = []
        self.disconnect_list = []
        self.vital_loop = []
        
        self.read_packet_list = []
        self.write_packet_list=[]
        
        if file_test:
            self.file_write_ble = file.File()

    def root_connect(self, root):
        self.root = root

    def scan_init(self):
        self.root.scanlistbox_init()
        self.scanlist = []
        
    # click한 client device의 index 를 return
    def get_index_select_client(self, address):
        for i in range(len(self.connected_client_list)):
            if self.connected_client_list[i].address == address:
                return i
        print("[NOTIFICATION] Disconnected Device !")
        return -1

    def check_same_client(self, list, data):
        for l in list:
            if l.address == data:
                return True
        return False

    def get_is_running(self):
        return self.is_running
    """
    callback function
    """  

    # scan 한 device의 name에서 'DGSB'가 포함된 device를 list에 담기 
    def scan_detection_callback(self, device, advertisement_data):
        if device.name is not None and "DGSB" in device.name:
            device_info = f'{device.name} {device.address}'
            if device_info not in self.scanlist:
                self.scanlist.append(device_info)
                self.root.scanlist_insert(len(self.scanlist)-1, device_info)

    # BLE 연결이 끊어진 경우 호출되는 함수.
    def ble_disconnect_callback(self, client):
        
        print("[BLE CALLBACK] Client with address {} got disconnected!".format(client.address))
        self.root.state_label_set(f'Disconnect ! {client.address}')
        self.root.clientlistbox_find_delete(client.address)
        if client.address not in self.disconnect_list:
            self.disconnect_list.append(client.address)
        if client.address in self.vital_loop:
            self.vital_loop.remove(client.address)

        if client in self.connected_client_list:
            self.connected_client_list.remove(client)

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

    def do_ble_connect_tasks(self, address):
        print("[BTN EVENT] BLE CONNECT")
        threading.Thread(target=self.asyncio_ble_connect_thread, args=(address,)).start()
    
    def do_ble_disconnect_tasks(self, address):
        print("[BTN EVENT] BLE DISCONNECT")
        threading.Thread(target=self.asyncio_ble_disconnect_thread, args=(address,)).start()
    
    def do_ble_write_tasks(self, address, packet):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_thread, args=(address, packet,)).start()

    def do_ble_write_loop_tasks(self, address, packet, time):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(target=self.asyncio_ble_write_loop_thread, args=(address, packet,time,)).start()
    """
    asyncio thread function
    """  
    # Asynchronous loop start -> BLE program start
    def asyncio_thread(self):
        self.loop.run_until_complete(self.asyncio_start()) 
        self.loop.close()
        self.root.change_ui(self.is_running)

    # Asynchronous loop stop -> BLE program stop
    def asyncio_stop_thread(self):
        if self.is_running:
            self.loop.create_task(self.asyncio_stop())
        else :
            print("[NOTIFICATION] It is not currently asynchronous.")

    def asyncio_scan_thread(self):
        self.loop.create_task(self.ble_scan())

    def asyncio_scan_stop_thread(self):
        self.loop.create_task(self.ble_scan_stop())

    def asyncio_ble_connect_thread(self, address):
        if address :
            self.loop.create_task(self.ble_connect(address))
        
    def asyncio_ble_disconnect_thread(self, address):
        if address:
            self.loop.create_task(self.ble_disconnect(address))   

    def asyncio_ble_write_thread(self, address, packet):
        if address:
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                if self.connected_client_list[index].address in self.vital_loop: # 현재 while문으로 write loop가 돌고 있다면 while stop
                    self.vital_loop.remove(self.connected_client_list[index].address)
                self.loop.create_task(self.ble_write_check(self.connected_client_list[index], packet, address.split(' ')[0]))

    def asyncio_ble_write_loop_thread(self, address, packet, time):
        if address:
            index = self.get_index_select_client(address.split(' ')[1])
            if index >= 0 :
                if self.connected_client_list[index].address in self.vital_loop: # 현재 while문으로 write loop가 돌고 있다면 while stop
                    self.vital_loop.remove(self.connected_client_list[index].address)
                else:
                    self.vital_loop.append(self.connected_client_list[index].address) # while문이 돌고 있지 않은 상태라면 while start
                    self.loop.create_task(self.ble_write_loop(self.connected_client_list[index], packet, time, address.split(' ')[0]))

    # Asynchronous BLE Program Start
    async def asyncio_start(self):
        if not self.is_running: 
            self.is_running = True
            self.root.change_ui(self.is_running)
            while self.is_running: # BLE Program 이 시작되면 비동기로 read list를 계속 체크함.
                await self.ble_read_packet_list_thread()

    # Asynchronous BLE Program Stop
    async def asyncio_stop(self):
        await self.ble_scan_stop() #scan 상태라면 stop 시켜줌
        await self.ble_all_disconnect() #연결된 모든 band 연결 해제
        await asyncio.sleep(2)
        self.is_running = False

    """
    ble function
    """  
    # Asynchronous BLE Scan Start
    async def ble_scan(self):
        if not self.is_scanning : 
            self.scan_init()
            self.scanner = BleakScanner()
            self.scanner.register_detection_callback(self.scan_detection_callback)
            await self.scanner.start()
            self.root.scan_state_label_set("Scanning..")
            self.is_scanning = True

    # Asynchronous BLE Scan Stop
    async def ble_scan_stop(self):
        if self.is_scanning:
            await self.scanner.stop()  
            self.is_scanning = False  
            self.root.scan_state_label_set("Scan Stop")
    
    # Asynchronous BLE Connect Function
    async def ble_connect(self, client_info):
        self.root.state_label_set(f"Connecting.. {client_info.split(' ')[1]}")
        if not self.check_same_client(self.connected_client_list, client_info.split(' ')[1]): # 현재 연결 돼있는지 체크
            client = BleakClient(client_info.split(' ')[1])
            try:
                client.set_disconnected_callback(self.ble_disconnect_callback)
                await client.connect()
                print("[BLE] Connect Success!")
                await asyncio.sleep(1)
                self.connected_client_list.append(client) # 연결된 client 는 list에 추가
                self.root.clientlistbox_insert(len(self.connected_client_list)-1, client_info)
                self.root.state_label_set(f"Connected {client.address}")
                await asyncio.sleep(1) 
                await self.ble_read_thread(client, client_info.split(' ')[0]) # client 가 연결되고 나면 read를 체크하는 thread 실행
            except Exception as e:
                self.root.messagebox_showwarning(f"[ERR] : {e} \n비정상적으로 연결이 해제된 경우 밴드와 앱을 재시작 해주세요.")
                print('[ERR] : ', e)
        else:
            print("[BLE] Already connected")
    
    # BLE Disconnect
    async def ble_disconnect(self, address): 
        for i in range(len(self.connected_client_list)) :
            if self.connected_client_list[i].address == address.split(' ')[1]: # 연결 리스트에서 같은 address인 data 찾기
                if self.connected_client_list[i].address not in self.disconnect_list: # 연결 종료 리스트 안에 있는 지 체크
                    self.disconnect_list.append(self.connected_client_list[i].address) # 없다면 넣기
                    await self.connected_client_list[i].disconnect() # 실제 연결 종료 함수 호출
                    await asyncio.sleep(1)
                    break

    # All Connected Client Disconnect
    async def ble_all_disconnect(self):
        temp_list = self.connected_client_list.copy()
        for i in range(len(temp_list)) :
            self.vital_loop = []
            
            self.disconnect_list.append(temp_list[i].address)
            await temp_list[i].disconnect()
            await asyncio.sleep(1)
            
    # BLE Write 
    async def ble_write(self, client, data, name):
        for w in self.write_packet_list: # write한 패킷의 응답이 없을 경우, write 할 수 없음.
            if w['address']==client.address:
                self.root.messagebox_showwarning(f"{client.address}로 보낸 패킷의 응답이 오지 않아 패킷을 보낼 수 없습니다.")
                print(f"[BLE WRITE] No response from packets sent by {name}.")
                return
        hex_data = print_hex(data)
        print(f"[BLE WRITE] {name} : {hex_data}")
        if file_test:
            self.file_write_ble.file_write_time("WRITE", hex_data)
        self.write_packet_list.append({'address':client.address,
            'data':data, 
            'datetime':datetime.now()})
        await client.write_gatt_char(read_write_charcteristic_uuid,  data) # 실제 band로 write 함.

    # write packet의 길이를 체크 하여 20 byte씩 쪼개서 보내도록 함.
    async def ble_write_check(self, client, data, name): 
        if len(data)>=21:

            await self.ble_write(client, data[0:20], name)
            await self.ble_write_check(data[20:len(data)])
        else:
            await self.ble_write(client, data, name)

    # 설정한 시간 초 마다 write loop가 도는 함수
    async def ble_write_loop(self, client, data, time, name):
        try:
            while  client.address in self.vital_loop:
                await self.ble_write_check(client, data, name)
                await asyncio.sleep(time)
        except:
            pass

    # BLE Read
    async def ble_read(self, client, name):
        if client.address not in self.disconnect_list:
            self.read_packet_list.append(  # 실제 data read하는 함수. read_packet_list에 read된 데이터 추가.
                {'address':client.address,
                'data':await client.read_gatt_char(read_write_charcteristic_uuid),
                'name':name})
        

    # connect 시작 후 0.1초마다 read 함. 
    async def ble_read_thread(self, client, name): 
        while client.address not in self.disconnect_list:
            await self.ble_read(client, name)
            await asyncio.sleep(0.1)
        del self.disconnect_list[self.disconnect_list.index(client.address)]
        
    # read_packet_list를 체크 하는 thread
    async def ble_read_packet_list_thread(self): 
        await asyncio.sleep(0.01)
        delete_list=[]
        for wi in range(len(self.write_packet_list)): # 5초 이내로 응답 없을 경우, time out으로 처리. 측정 시작인 경우에는 30초.
            time = 5
            if self.write_packet_list[wi]['data'][1]==65:
                time = 30
            else :
                time = 5
            if (datetime.now()-self.write_packet_list[wi]['datetime']).seconds>time:
                print("[BLE READ] Response Time Out")
                delete_list.append(wi)
        for r in self.read_packet_list: 
            if r['data'] != bytearray():
                for wi in range(len(self.write_packet_list)):
                    if (self.write_packet_list[wi]['address'] == r['address']) : # write한 패킷의 응답이 왔는 지 체크
                        if wi not in delete_list:
                            delete_list.append(wi)
                        break
                hex_data = print_hex(r['data']) 
                print(f"[BLE READ] {r['name']} : {hex_data}")
                protocol.ble_read_parsing(r['data'], r['name']) # 실제 데이터 파싱하는 함수 호출
                if file_test:
                    self.file_write_ble.file_write_time("READ",hex_data)
        for d in delete_list:
            del self.write_packet_list[d]
        self.read_packet_list.clear() 




