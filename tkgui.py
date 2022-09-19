from tkinter import DISABLED, NORMAL, Tk, Label, Button, StringVar, constants, Frame, Listbox, Scrollbar, Text, messagebox, font
import ble as b
import protocol

class TkGUI:
    def __init__(self):
        self.root = Tk()
        self.loop = b.BLE()

        """
        root 
        """
        self.root.title("BLE TEST")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("1080x600")

        """
        program button
        """
        self.ble_start_btn = Button(self.root, text="PROGRAM START", bg='green', fg='white', font=font.Font(size=12, weight="bold"), command=self.loop.do_asyncio_tasks)
        self.ble_stop_btn = Button(self.root, text="PROGRAM STOP", bg='green', fg='white', font=font.Font(size=12, weight="bold"), command=self.loop.do_asyncio_stop_tasks)
        self.ble_stop_btn.pack(side="bottom")
        """
        scan frame
        Left Area : BLE Scan 및 Connect 하는 영역
        """
        self.frame_scan = Frame(self.root)
        self.scan_state_text = StringVar()
        self.scan_state_label = Label(self.frame_scan, font=font.Font(size=10, weight="bold"), textvariable=self.scan_state_text)
        self.scan_btn = Button(self.frame_scan, text="BLE Scan", command=self.loop.do_scan_tasks)
        self.scan_stop_btn = Button(self.frame_scan, text="BLE Scan Stop", command=self.loop.do_scan_stop_tasks)
        self.connect_btn = Button(self.frame_scan, text="BLE Connect", command=lambda:self.loop.do_ble_connect_tasks(self.scanlistbox_return()))
        
        self.title_scan_list = Label(self.frame_scan, text="SCAN LIST",font=font.Font(size=10, weight="bold"))
        self.frame_scan_list = Frame(self.frame_scan)
        self.scrollbar = Scrollbar(self.frame_scan_list, orient="vertical")
        self.scanlistbox = Listbox(self.frame_scan_list, selectmode='browse', yscrollcommand=self.scrollbar.set, height=10, width=45)
        """
        scan frame show
        """
        self.scan_state_label.grid(row=0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )     
        self.scan_btn.grid(row=1, column=0, sticky=constants.W)
        self.scan_stop_btn.grid(row=1, column=1, sticky=constants.W)
        self.connect_btn.grid(row=1, column=2, sticky=constants.W)
        self.title_scan_list.grid(row=2, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )     
        self.frame_scan_list.grid(row=3, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.scanlistbox.pack(expand=True, fill=constants.Y)
        """
        connect frame
        Right Area : BLE 연결 후 연결해제 및 통신하는 영역
        """
        self.frame_connect = Frame(self.root)
        self.state_text = StringVar()
        self.state_label = Label(self.frame_connect, font=font.Font(size=10, weight="bold"), textvariable=self.state_text)
        self.disconnect_btn = Button(self.frame_connect, text="BLE Disconnect", command=lambda:self.loop.do_ble_disconnect_tasks(self.clientlistbox_return()))
        self.measure_btn = Button(self.frame_connect, text="Measure Start", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(), protocol.REQ_START_MEASURE))
        self.stop_btn = Button(self.frame_connect, text="Measure Stop", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_STOP_MEASURE))
        
        self.get_hr_btn = Button(self.frame_connect, text="GET HR", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_HR))
        self.get_spo2_btn = Button(self.frame_connect, text="GET SPO2", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_SPO2))
        self.get_walk_run_step_btn = Button(self.frame_connect, text="GET WALK/RUN_STEP", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_WALK_RUN))
        self.get_motion_flag = Button(self.frame_connect, text="GET MOTION_FLAG", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_MOTION_FLAG))
        self.get_activity = Button(self.frame_connect, text="GET ACTIVITY", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_ACTIVITY))
        
        
        self.get_battery_btn = Button(self.frame_connect, text="GET BATTERY", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_BATT))
        self.get_scd_btn = Button(self.frame_connect, text="GET SCD", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_SCD))
        self.get_acc_btn = Button(self.frame_connect, text="GET ACC", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_ACC))
        self.get_gyro_btn = Button(self.frame_connect, text="GET GYRO", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_GYRO))
        
        self.get_falldetect = Button(self.frame_connect, text="GET FALL_DETECT", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_FALL_DETECT))
        self.get_temperature = Button(self.frame_connect, text="GET TEMP", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_TEMP))
        self.get_pressure = Button(self.frame_connect, text="GET PRESSURE", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_PRESSURE))

        self.get_all_btn = Button(self.frame_connect, text="GET ALL", command=lambda:self.loop.do_ble_write_tasks(self.clientlistbox_return(),protocol.REQ_GET_ALL_DATA))
        self.get_all_continue = Button(self.frame_connect, text="GET ALL Continue",command=lambda:self.loop.do_ble_write_loop_tasks(self.clientlistbox_return(), protocol.REQ_GET_ALL_DATA, 1))
        
        self.file_test_text = StringVar()
        self.file_test_text.set("CSV ON")
        
        self.file_test = Button(self.frame_connect, textvariable=self.file_test_text, command=self.setting_file_test)
        self.read_text = StringVar()
        self.read_text.set("READ DATA : ")
        self.write_text = StringVar()
        self.write_text.set("WRITE DATA : ")   

        self.write_label=Label(self.frame_connect, textvariable=self.write_text)
        self.read_label=Label(self.frame_connect, textvariable=self.read_text)
        
        self.title_connected_device_list = Label(self.frame_connect, text="Connected Device List",font=font.Font(size=10, weight="bold"))
        self.client_frame = Frame(self.frame_connect)
        self.client_scrollbar = Scrollbar(self.client_frame, orient="vertical")
        self.client_listbox = Listbox(self.client_frame, selectmode='browse', yscrollcommand=self.client_scrollbar.set, height=5, width=40)

        self.label=Label(self.frame_connect, text="Packet Input ex) 0x02 0x01 0x01 0x01 0x03")
        self.input_text=Text(self.frame_connect, height=5)
        self.submit_btn = Button(self.frame_connect, text="Submit", command=lambda:self.submit_button(self.clientlistbox_return())) # 입력한 packet을 write 함.
        
        self.frame_empty = Frame(self.frame_connect)

        self.hr_text = StringVar()
        self.frame_hr = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_hr = Label(self.frame_hr, text="90", width = 10, height=2, textvariable=self.hr_text,font=font.Font(size=8))
        self.label_hr_title = Label(self.frame_hr, text="HR", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.spo2_text = StringVar()
        self.frame_spo2 = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_spo2 = Label(self.frame_spo2, text="90", width = 10, height=2, textvariable=self.spo2_text,font=font.Font(size=8))
        self.label_spo2_title = Label(self.frame_spo2, text="SpO2", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.battery_text = StringVar()
        self.frame_battery = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_battery = Label(self.frame_battery, text="90", width = 10, height=2, textvariable=self.battery_text,font=font.Font(size=8))
        self.label_battery_title = Label(self.frame_battery, text="Battery", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.accx_text = StringVar()
        self.frame_accx = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_accx = Label(self.frame_accx, text="90", width = 10, height=2, textvariable=self.accx_text,font=font.Font(size=8))
        self.label_accx_title = Label(self.frame_accx, text="ACC X", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        
        self.accy_text = StringVar()
        self.frame_accy = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_accy = Label(self.frame_accy, text="90", width = 10, height=2, textvariable=self.accy_text,font=font.Font(size=8))
        self.label_accy_title = Label(self.frame_accy, text="ACC Y", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.accz_text = StringVar()
        self.frame_accz = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_accz = Label(self.frame_accz, text="90", width = 10, height=2, textvariable=self.accz_text,font=font.Font(size=8))
        self.label_accz_title = Label(self.frame_accz, text="ACC Z", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.gyrox_text = StringVar()
        self.frame_gyrox = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_gyrox = Label(self.frame_gyrox, text="90", width = 10, height=2, textvariable=self.gyrox_text,font=font.Font(size=8))
        self.label_gyrox_title = Label(self.frame_gyrox, text="Gyro X", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        
        self.gyroy_text = StringVar()
        self.frame_gyroy = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_gyroy = Label(self.frame_gyroy, text="90", width = 10, height=2, textvariable=self.gyroy_text,font=font.Font(size=8))
        self.label_gyroy_title = Label(self.frame_gyroy, text="Gyro Y", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        self.gyroz_text = StringVar()
        self.frame_gyroz = Frame(self.frame_connect,borderwidth = 2,relief="ridge", width=20, height =10)
        self.label_gyroz = Label(self.frame_gyroz, text="90", width = 10, height=2, textvariable=self.gyroz_text,font=font.Font(size=8))
        self.label_gyroz_title = Label(self.frame_gyroz, text="Gyro Z", width = 10, height=2,font=font.Font(size=9, weight="bold"))

        """
        connect frame show
        """
        self.state_label.grid(row=0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        
        self.disconnect_btn.grid(row=1, column=0, sticky=constants.W)
        self.measure_btn.grid(row=1,column=1,  sticky=constants.W)
        self.stop_btn.grid(row=1, column=2, sticky=constants.W)
        
        self.get_hr_btn.grid(row=2, column=0, sticky=constants.W)
        self.get_spo2_btn.grid(row=2, column=1, sticky=constants.W)
        self.get_walk_run_step_btn.grid(row=2, column=2, sticky=constants.W)
        
        self.get_motion_flag.grid(row=3, column=0, sticky=constants.W)
        
        self.get_activity.grid(row=3, column=1, sticky=constants.W)
        self.get_battery_btn.grid(row=3, column=2, sticky=constants.W)
        self.get_scd_btn.grid(row=4, column=0, sticky=constants.W)
        self.get_acc_btn.grid(row=4, column=1, sticky=constants.W)
        self.get_gyro_btn.grid(row=4, column=2, sticky=constants.W)
        self.get_falldetect.grid(row=5, column=0, sticky=constants.W)
        self.get_temperature.grid(row=5, column=1, sticky=constants.W)
        self.get_pressure.grid(row=5, column=2, sticky=constants.W)

        self.get_all_btn.grid(row=6, column=0, sticky=constants.W)
        self.get_all_continue.grid(row=6, column=1, sticky=constants.W)
        self.file_test.grid(row=6, column=2, sticky=constants.W)
        self.title_connected_device_list.grid(row=7, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.client_frame.grid(row=8, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        self.client_scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.client_listbox.pack(expand=True, fill=constants.Y)
        
        # self.label.grid(row=9, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        # self.input_text.grid(row=10, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        # self.submit_btn.grid(row=11, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)


        self.frame_empty.grid(row = 9, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S, padx=10, pady=10)
        self.frame_hr.grid(row = 10, column = 0)
        self.label_hr.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_hr_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_spo2.grid(row = 10, column = 1)
        self.label_spo2.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_spo2_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_battery.grid(row = 10, column = 2)
        self.label_battery.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_battery_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_accx.grid(row = 11, column = 0)
        self.label_accx.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_accx_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_accy.grid(row = 11, column = 1)
        self.label_accy.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_accy_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_accz.grid(row = 11, column = 2)
        self.label_accz.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_accz_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_gyrox.grid(row = 12, column = 0)
        self.label_gyrox.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_gyrox_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )

        self.frame_gyroy.grid(row = 12, column = 1)
        self.label_gyroy.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_gyroy_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        
        self.frame_gyroz.grid(row = 12, column = 2)
        self.label_gyroz.grid(row = 0, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.label_gyroz_title.grid(row = 1, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.loop.root_connect(self)
        self.change_ui(False)

    def run(self):
        self.root.mainloop()

    # tkinter close callback
    def on_closing(self):
        if self.loop.get_is_running() :
            messagebox.showinfo("프로그램 종료", "하단에 \'BLE STOP\' 버튼을 누른 후 종료해주세요.")
        else :
            self.root.destroy()

    """
    tkinter ui change function
    """
    def change_ui(self, is_running):
        if is_running:
            
            self.ble_start_btn.pack_forget()
            
            self.scan_frame_show()
            self.connect_frame_show()
            
        else:
            self.state_label_set("IDLE")
            self.scan_state_label_set("IDLE")

            self.scanlistbox_init()
           
            self.scan_frame_hide()
            self.connect_frame_hide()
            self.ble_start_btn.pack()


    def scan_frame_show(self):
        self.frame_scan.pack(side="left", fill="both", expand=True)


    def scan_frame_hide(self):
        self.frame_scan.pack_forget()

        
    def connect_frame_show(self):
        self.frame_connect.pack(side="right", fill="both", expand=True)
        self.ble_stop_btn['state'] = NORMAL

    def connect_frame_hide(self):
        self.frame_connect.pack_forget()
        self.ble_stop_btn['state'] = DISABLED

    """
    label set function
    """  
    def state_label_set(self, messeage):
        self.state_text.set(f"BLE state :  {messeage}")

    def scan_state_label_set(self, messeage):
        self.scan_state_text.set(f"SCAN state : {messeage}")

    def read_label_set(self, data):
        self.read_text.set(f"READ DATA : {data}")

    def write_label_set(self, data):
        self.write_text.set(f"WRITE DATA : {data}")

    def band_data_label_set(self, hr, spo2, battery, accx, accy, accz, gyrox, gyroy, gyroz):
        self.hr_text.set(f"{hr}")
        self.spo2_text.set(f"{spo2}")
        self.battery_text.set(f"{battery}")
        self.accx_text.set(f"{accx}")
        self.accy_text.set(f"{accy}")
        self.accz_text.set(f"{accz}")
        self.gyrox_text.set(f"{gyrox}")
        self.gyroy_text.set(f"{gyroy}")
        self.gyroz_text.set(f"{gyroz}")
    """
    listbox function
    """  
    def scanlistbox_init(self):
        self.scanlistbox.delete(0, constants.END)

    def scanlist_insert(self, num, info):
        self.scanlistbox.insert(num, info)

    def scanlistbox_return(self):
        for i in self.scanlistbox.curselection():
            return self.scanlistbox.get(i)
        print("[NOTIFICATION] Please select ble device !")
        return None

    def clientlistbox_insert(self, num, info):
        self.client_listbox.insert(num, info)

    def clientlistbox_return(self):
        for i in self.client_listbox.curselection():
            return self.client_listbox.get(i)
        print("[NOTIFICATION] Please select ble device !")
        return None

    def clientlistbox_index_delete(self, index):
        self.client_listbox.delete(index)

    def clientlistbox_find_delete(self, address):
        for i in range(self.client_listbox.size()):
            if address in self.client_listbox.get(i):
                self.clientlistbox_index_delete(i)
                break
    """
    button function
    """  
    def submit_button(self, address):
        input_text = self.input_text.get(1.0, constants.END+"-1c")
        if len(input_text) != 0:
            input_text = input_text.split(" ")
            submit_packet = []
            for i in input_text:
                submit_packet.append(int(i, 16))
            self.loop.do_ble_write_tasks( address, bytearray(submit_packet))


    def setting_file_test(self):
        if protocol.file_test :
            protocol.file_test = False
            self.file_test_text.set("CSV ON")
        else :
            protocol.file_test = True
            self.file_test_text.set("CSV OFF")
