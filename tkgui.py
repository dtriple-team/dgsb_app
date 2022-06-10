from tkinter import Tk, Label, Button, StringVar, constants, Frame, Listbox, Scrollbar, Text
import ble as b
import time,sys 
import threading
class TkGUI:
    def __init__(self):
        self.root = Tk()
        self.loop = b.BLE()
        self.root.title("GUI TEST")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("1080x600")
        self.is_close = False
        self.ble_start_btn = Button(self.root, text="BLE START", command=self.loop.do_asyncio_tasks)
        self.ble_stop_btn = Button(self.root, text="BLE STOP", command=self.loop.do_asyncio_stop_tasks)
        
        self.status_text = StringVar()
        self.status_text.set("STATUS : IDLE")
        self.status_label = Label(self.root, textvariable=self.status_text)
        
        
        self.frame_scan = Frame(self.root)
        self.frame_scan.pack(side="left", fill="both", expand=True)
        
        
        self.scan_btn = Button(self.frame_scan, text="BLE Scan", command=self.loop.do_scan_tasks)
        self.scan_stop_btn = Button(self.frame_scan, text="BLE Scan Stop", command=self.loop.do_scan_stop_tasks)
        self.connect_btn = Button(self.frame_scan, text="BLE Connect", command=self.loop.do_ble_connect_tasks)
        self.frame = Frame(self.frame_scan)
        self.scrollbar = Scrollbar(self.frame, orient="vertical")
        self.devicelistbox = Listbox(self.frame, selectmode='extended', yscrollcommand=self.scrollbar.set, height=0)
        
        # # -----------------------------------------------------------------------------------------
        self.frame_connect = Frame(self.root)
        self.frame_connect.pack(side="right", fill="both", expand=True)
        self.close_btn = Button(self.frame_connect, text="BLE Disconnect", command=self.loop.do_ble_disconnect_tasks)

        self.measure_btn = Button(self.frame_connect, text="Measure Start", command=lambda:self.loop.do_ble_write_tasks(bytearray([0x02, 0x03])))
        self.stop_btn = Button(self.frame_connect, text="Measure Stop")
        self.get_hr_btn = Button(self.frame_connect, text="GET HR")
        self.get_spo2_btn = Button(self.frame_connect, text="GET SPO2")

        self.random_btn = Button(self.frame_connect, text="Random Data")
        
        self.read_text = StringVar()
        self.read_text.set("READ DATA : ")

        self.write_text = StringVar()
        self.write_text.set("WRITE DATA : ")   

        self.write_label=Label(self.frame_connect, textvariable=self.write_text)
        self.read_label=Label(self.frame_connect, textvariable=self.read_text)

        self.client_frame = Frame(self.frame_connect)
        self.client_scrollbar = Scrollbar(self.client_frame, orient="vertical")
        self.client_listbox = Listbox(self.client_frame, selectmode='extended', yscrollcommand=self.scrollbar.set, height=0)
        
        self.label=Label(self.frame_connect, text="Packet Input ex) 0x02 0x01 0x01 0x01 0x03")
        
        self.text=Text(self.frame_connect)
        self.submit_btn = Button(self.frame_connect, text="Submit")
        
        self.loop.root_connect(self)
        
        self.change_ui(False)
    def run(self):
        # self.change_ui(False)
        self.root.mainloop()

    def on_closing(self):
        self.is_close = True
        t1 = self.loop.do_asyncio_close_tasks()
        t2 = threading.Thread(target=self.close)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    def get_close_status(self):
        return self.is_close
    def close(self):
        print("종료 !!")
        while self.loop.is_running:
            print("..?")
            time.sleep(2)
        self.root.destroy() 
    def change_ui(self, is_running):
        if is_running:
            self.ble_start_btn.pack_forget()
            self.ble_stop_btn.pack(side="bottom", fill="x")
            self.status_label.pack(side="top", fill="x")
            self.before_connect_show()
            self.after_connect_show()
            
        else:
            self.ble_stop_btn.pack_forget()
            self.status_label.pack_forget()
            self.before_connect_hide()
            self.after_connect_hide()
            self.ble_start_btn.pack(side="top", fill="x")
    def before_connect_show(self):

        self.scan_btn.grid(row=1, column=0, sticky=constants.W)
        self.scan_stop_btn.grid(row=1, column=1, sticky=constants.W)
        self.connect_btn.grid(row=1, column=2, sticky=constants.W)
        self.frame.grid(row=2, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.devicelistbox.pack(expand=True, fill=constants.Y)


    def before_connect_hide(self):

        self.scan_btn.grid_forget()
        self.scan_stop_btn.grid_forget()
        self.connect_btn.grid_forget()
        self.frame.grid_forget()
        self.scrollbar.pack_forget()
        self.devicelistbox.pack_forget()
        
    def after_connect_show(self):

        self.close_btn.grid(row=1, column=0, sticky=constants.W)
        self.measure_btn.grid(row=1,column=1,  sticky=constants.W)
        self.stop_btn.grid(row=1, column=2, sticky=constants.W)
        self.get_hr_btn.grid(row=2, column=0, sticky=constants.W)
        self.get_spo2_btn.grid(row=2, column=1, sticky=constants.W)
        self.random_btn.grid(row=2, column=2, sticky=constants.W)
        self.write_label.grid(row=3, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.read_label.grid(row=4, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        
        self.client_frame.grid(row=5, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        self.client_scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.client_listbox.pack(expand=True, fill=constants.Y)
        
        self.label.grid(row=6, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        self.text.grid(row=7, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        self.submit_btn.grid(row=8, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S)
        
        
    def after_connect_hide(self):

        self.close_btn.grid_forget()
        self.measure_btn.grid_forget()
        self.stop_btn.grid_forget()
        self.get_hr_btn.grid_forget()
        self.get_spo2_btn.grid_forget()
        self.random_btn.grid_forget()
        self.write_label.grid_forget()
        self.read_label.grid_forget()
        self.client_frame.grid_forget()
        self.client_scrollbar.pack_forget()
        self.client_listbox.pack_forget()
        self.label.grid_forget()
        self.text.grid_forget()
        self.submit_btn.grid_forget()

    def status_label_set(self, messeage):
        self.status_text.set(messeage)

    def read_label_set(self, data):
        self.read_text.set(f"READ DATA : {data}")

    def write_label_set(self, data):
        self.write_text.set(f"WRITE DATA : {data}")

    def devicelistbox_init(self):
        self.devicelistbox.delete(0, constants.END)

    def devicelist_insert(self, num, info):
        self.devicelistbox.insert(num, info)

    def devicelistbox_return(self):
        for i in self.devicelistbox.curselection():
            return self.devicelistbox.get(i)
        return None

    def devicelistbox_selete_delete(self):
        for i in self.devicelistbox.curselection():
            self.devicelistbox.delete(i)
            break


    def clientlistbox_insert(self, num, info):
        self.client_listbox.insert(num, info)

    def clientlistbox_return(self):
        for i in self.client_listbox.curselection():
            return self.client_listbox.get(i)
        return None

    def clientlistbox_index_return(self):
        for i in self.client_listbox.curselection():
            return i
    def clientlistbox_selete_delete(self):
        self.client_listbox.delete(self.clientlistbox_index_return())
        
    def clientlistbox_index_delete(self, index):
        self.client_listbox.delete(index)

    def clientlistbox_find_delete(self, address):
        for i in range(self.client_listbox.size()):
            if address in self.client_listbox.get(i):
                self.clientlistbox_index_delete(i)
                break
    def clientlistbox_all_delete(self):
        self.client_listbox.delete(0, constants.END)
my_gui = TkGUI()
my_gui.run()

