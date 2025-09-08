import asyncio
import threading
import file
import protocol
from bleak import BleakClient, BleakScanner  # BLE 통신을 위한 모듈
from ble_print import print_hex
from datetime import datetime

file_test = False  # True-> write, read packet을 file로 확인할 수 있음
read_write_charcteristic_uuid = "f0001111-0451-4000-b000-000000000000"


class BLE:
    def __init__(self):
        self.loop = None  # BLE와 통신하기 위한 Asynchronous loop 변수
        self.root = None  # gui를 제어하기 위해 사용되는 root 변수
        self.is_running = False  # 비동기 loop가 실행중인지 체크

        # BLE scan에 사용되는 변수들
        self.scanner = None
        self.is_scanning = False
        self.scanlist = []

        self.connected_client_list = []
        self.connected_client_file_list = []
        self.disconnect_list = []
        self.vital_loop = []

        self.read_packet_list = []
        self.write_packet_list = []

        if file_test:
            self.file_write_ble = file.File()

    def init(self):
        self.disconnect_list = []
        self.vital_loop = []
        self.read_packet_list = []
        self.write_packet_list = []

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

    def check_same_client(self, list_, data):
        for l in list_:
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
            device_info = f"{device.name} {device.address}"
            if device_info not in self.scanlist:
                self.scanlist.append(device_info)
                if self.root:
                    self.root.scanlist_insert(
                        len(self.scanlist) - 1, device_info)

    # BLE 연결이 끊어진 경우 호출되는 함수.
    def ble_disconnect_callback(self, client):
        print(
            "[BLE CALLBACK] Client with address {} got disconnected!".format(
                client.address
            )
        )
        if self.root:
            self.root.state_label_set(f"Disconnect ! {client.address}")
            self.root.clientlistbox_find_delete(client.address)

        if client.address not in self.disconnect_list:
            self.disconnect_list.append(client.address)

        if client.address in self.vital_loop:
            self.vital_loop.remove(client.address)

        for w in list(self.write_packet_list):
            if w["address"] == client.address:
                self.write_packet_list.remove(w)
                break

        if client in self.connected_client_list:
            idx = self.connected_client_list.index(client)
            if idx < len(self.connected_client_file_list):
                self.connected_client_file_list.pop(idx)
            self.connected_client_list.remove(client)

    """
    thread task function
    """

    def do_asyncio_tasks(self):
        print("[BTN EVENT] PROGRAM START")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.asyncio_thread, daemon=True).start()

    def do_asyncio_stop_tasks(self):
        print("[BTN EVENT] PROGRAM STOP")
        threading.Thread(target=self.asyncio_stop_thread, daemon=True).start()

    def do_scan_tasks(self):
        print("[BTN EVENT] SCAN START")
        threading.Thread(target=self.asyncio_scan_thread, daemon=True).start()

    def do_scan_stop_tasks(self):
        print("[BTN EVENT] SCAN STOP")
        threading.Thread(target=self.asyncio_scan_stop_thread,
                         daemon=True).start()

    def do_ble_connect_tasks(self, address):
        print("[BTN EVENT] BLE CONNECT")
        threading.Thread(
            target=self.asyncio_ble_connect_thread, args=(
                address,), daemon=True
        ).start()

    def do_ble_disconnect_tasks(self, address):
        print("[BTN EVENT] BLE DISCONNECT")
        threading.Thread(
            target=self.asyncio_ble_disconnect_thread, args=(
                address,), daemon=True
        ).start()

    def do_ble_write_tasks(self, address, packet):
        print("[BTN EVENT] BLE WRITE")
        threading.Thread(
            target=self.asyncio_ble_write_thread, args=(
                address, packet,), daemon=True
        ).start()

    def do_ble_write_loop_tasks(self, address, packet, time):
        print("[BTN EVENT] BLE WRITE LOOP")
        threading.Thread(
            target=self.asyncio_ble_write_loop_thread,
            args=(address, packet, time,),
            daemon=True,
        ).start()

    """
    asyncio thread function
    """
    # Asynchronous loop start -> BLE program start

    def asyncio_thread(self):
        # 루프가 도는 스레드에서 반드시 set_event_loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncio_start())
        self.loop.close()
        if self.root:
            self.root.change_ui(self.is_running)  # 처음화면으로 GUI 변경

    # Asynchronous loop stop -> BLE program stop
    def asyncio_stop_thread(self):
        if self.is_running and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.asyncio_stop(), self.loop)
        else:
            print("[NOTIFICATION] It is not currently asynchronous.")

    def asyncio_scan_thread(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.ble_scan(), self.loop)

    def asyncio_scan_stop_thread(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.ble_scan_stop(), self.loop)

    def asyncio_ble_connect_thread(self, address):
        if address and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.ble_connect(address), self.loop)

    def asyncio_ble_disconnect_thread(self, address):
        if address and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.ble_disconnect(address), self.loop)

    def asyncio_ble_write_thread(self, address, packet):
        if address and self.loop:
            index = self.get_index_select_client(address.split(" ")[1])
            if index >= 0:
                # 현재 while문으로 write loop가 돌고 있다면 while stop
                if self.connected_client_list[index].address in self.vital_loop:
                    self.vital_loop.remove(
                        self.connected_client_list[index].address)
                asyncio.run_coroutine_threadsafe(
                    self.ble_write_check(
                        self.connected_client_list[index],
                        packet,
                        address.split(" ")[0],
                    ),
                    self.loop,
                )

    def asyncio_ble_write_loop_thread(self, address, packet, time):
        if address and self.loop:
            index = self.get_index_select_client(address.split(" ")[1])
            if index >= 0:
                if self.connected_client_list[index].address in self.vital_loop:
                    # 현재 while문으로 write loop가 돌고 있다면 while stop
                    self.vital_loop.remove(
                        self.connected_client_list[index].address)
                else:
                    # while문이 돌고 있지 않은 상태라면 while start
                    self.vital_loop.append(
                        self.connected_client_list[index].address)
                    asyncio.run_coroutine_threadsafe(
                        self.ble_write_loop(
                            self.connected_client_list[index],
                            packet,
                            time,
                            address.split(" ")[0],
                        ),
                        self.loop,
                    )

    # Asynchronous BLE Program Start
    async def asyncio_start(self):
        if not self.is_running:
            self.init()
            self.is_running = True
            if self.root:
                self.root.change_ui(self.is_running)  # BLE program 화면으로 GUI 변경
            while self.is_running:
                await self.ble_read_packet_list_thread()  # 비동기로 read list를 계속 체크

    # Asynchronous BLE Program Stop
    async def asyncio_stop(self):
        await self.ble_scan_stop()  # scan 상태라면 stop
        await self.ble_all_disconnect()  # 연결된 모든 band 연결 해제
        await asyncio.sleep(2)
        self.is_running = False  # BLE program 종료

    """
    ble function
    """
    # Asynchronous BLE Scan Start

    async def ble_scan(self):
        if not self.is_scanning:
            self.scan_init()
            # ⚠️ 경고 해결: 생성자에서 detection_callback 사용
            self.scanner = BleakScanner(
                detection_callback=self.scan_detection_callback)
            await self.scanner.start()
            if self.root:
                self.root.scan_state_label_set("Scanning..")
            self.is_scanning = True

    # Asynchronous BLE Scan Stop
    async def ble_scan_stop(self):
        if self.is_scanning and self.scanner:
            try:
                await self.scanner.stop()
            finally:
                self.is_scanning = False
                self.scanner = None
                if self.root:
                    self.root.scan_state_label_set("Scan Stop")

    # Asynchronous BLE Connect Function
    async def ble_connect(self, client_info):
        addr = client_info.split(" ")[1]
        if self.root:
            self.root.state_label_set(f"Connecting.. {addr}")
        if not self.check_same_client(self.connected_client_list, addr):  # 중복 체크
            client = BleakClient(addr)
            try:
                client.set_disconnected_callback(self.ble_disconnect_callback)
                await client.connect()
                await asyncio.sleep(1)
                print("[BLE] Connect Success!")
                if client.address in self.disconnect_list:
                    self.disconnect_list.remove(client.address)
                self.connected_client_list.append(client)  # 연결된 client list 추가
                self.connected_client_file_list.append(self.return_today())
                if self.root:
                    self.root.clientlistbox_insert(
                        len(self.connected_client_list) - 1, client_info
                    )
                    self.root.state_label_set(f"Connected {client.address}")
                # 연결 후 read 루프 시작
                await self.ble_read_thread(client, client_info.split(" ")[0])
            except Exception as e:
                print(
                    f"[ERR] : {e} 비정상적으로 연결이 해제된 경우 밴드와 앱을 재시작 해주세요."
                )
        else:
            print("[BLE] Already connected")

    # BLE Disconnect
    async def ble_disconnect(self, address):
        for cl in list(self.connected_client_list):
            if cl.address == address.split(" ")[1]:  # 동일 address
                if cl.address not in self.disconnect_list:
                    self.disconnect_list.append(cl.address)
                    await cl.disconnect()
                    await asyncio.sleep(1)
                    break

    # All Connected Client Disconnect
    async def ble_all_disconnect(self):
        try:
            temp_list = self.connected_client_list.copy()
            self.vital_loop = []
            self.write_packet_list = []
            for c in temp_list:
                self.disconnect_list.append(c.address)
                await c.disconnect()
                await asyncio.sleep(1)
        except Exception as e:
            print(f"[ERR] : {e}")
            pass

    async def ble_write_timeout_check(self, list_content, time_sec):
        try:
            i = 0
            count = int(time_sec / 0.5)
            while list_content in self.write_packet_list:
                if i >= count:
                    print("[BLE READ] Response Time Out")
                    try:
                        self.write_packet_list.remove(list_content)
                    except ValueError:
                        pass
                    break
                i += 1
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[ERR] : {e}")
            pass

    # BLE Write
    async def ble_write(self, client, data: bytes, name):
        # 응답 대기 중이면 쓰기 금지
        for w in self.write_packet_list:
            if w["address"] == client.address:
                print(
                    f"[BLE WRITE] No response from packets sent by {client.address}."
                )
                return
        hex_data = print_hex(data)
        print(f"[BLE WRITE] {client.address} : {hex_data}")
        if file_test:
            self.file_write_ble.file_write_time(
                "WRITE", client.address, hex_data)

        list_content = {"address": client.address, "data": data}
        self.write_packet_list.append(list_content)

        await client.write_gatt_char(read_write_charcteristic_uuid, data)

        # 패킷 타입에 따라 타임아웃 가변 (예: data[1] == 65 → 30초)
        timeout_sec = 30 if len(data) > 1 and data[1] == 65 else 5
        await self.ble_write_timeout_check(list_content, timeout_sec)

    # write packet 길이를 20 byte씩 분할 전송
    async def ble_write_check(self, client, data: bytes, name):
        # 빈 바이트 방어
        if not data:
            return
        # 20바이트 MTU 기준 분할
        offset = 0
        chunk = 20
        while offset < len(data):
            part = data[offset: offset + chunk]
            await self.ble_write(client, part, name)
            offset += chunk

    # 설정한 시간 초 마다 write loop가 도는 함수
    async def ble_write_loop(self, client, data, time_sec, name):
        try:
            while client.address in self.vital_loop:
                await self.ble_write_check(client, data, name)
                await asyncio.sleep(time_sec)
        except Exception:
            pass

    # BLE Read
    async def ble_read(self, client, name):
        if client.address not in self.disconnect_list:
            self.read_packet_list.append(
                {
                    "address": client.address,
                    "data": await client.read_gatt_char(
                        read_write_charcteristic_uuid
                    ),
                    "name": name,
                }
            )

    # connect 시작 후 0.1초마다 read 함.
    async def ble_read_thread(self, client, name):
        while client.address not in self.disconnect_list:
            await self.ble_read(client, name)
            await asyncio.sleep(0.1)
        # disconnect_list 소비
        try:
            self.disconnect_list.remove(client.address)
        except ValueError:
            pass

    # read_packet_list를 체크 하는 thread
    async def ble_read_packet_list_thread(self):
        try:
            await asyncio.sleep(0.01)
            delete_list = []
            for r in self.read_packet_list:
                if r["data"] != bytearray():
                    hex_data = print_hex(r["data"])
                    print(f"[BLE READ] {r['address']} : {hex_data}")
                    protocol.ble_read_parsing(
                        r,
                        self.root,
                        self.connected_client_file_list[
                            self.get_index_select_client(r["address"])
                        ],
                    )
                    if file_test:
                        self.file_write_ble.file_write_time(
                            "READ", r["address"], hex_data
                        )

            # write에 대한 응답 도착 시 대기열에서 제거
            for p in protocol.parsinglist:
                for wi in range(len(self.write_packet_list)):
                    if wi not in delete_list:
                        try:
                            if (
                                self.write_packet_list[wi]["address"] == p["address"]
                                and (
                                    p["data"][1]
                                    - self.write_packet_list[wi]["data"][1]
                                )
                                == 64
                            ):
                                delete_list.append(wi)
                                break
                        except Exception:
                            # 인덱스/형변환 방어
                            pass

            protocol.parsinglist = []
            self.read_packet_list.clear()

            # 역순 삭제
            for i, idx in enumerate(sorted(delete_list)):
                del self.write_packet_list[idx - i]

        except Exception as e:
            print(f"[Err] {e}")
            pass

    def return_today(self):
        today = str(datetime.now())
        return f"{today[:10]} {today[11:13]}-{today[14:16]}-{today[17:19]}"
