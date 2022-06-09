from tkinter import Tk, Label, Button, StringVar, constants, Frame, Listbox, Scrollbar, Text
import ble as b
class TkGUI:
    def __init__(self):
        self.root = Tk()
        self.loop = b.BLE()
        self.root.title("GUI TEST")
        self.root.geometry("1080x600")
        self.status_text = StringVar()
        self.status_text.set("STATUS : IDLE")
        self.status_label = Label(self.root, textvariable=self.status_text)
        self.status_label.pack()
        
        self.frame_scan = Frame(self.root)
        self.frame_scan.pack(side="left", fill="both", expand=True)
        
        
        self.scan_btn = Button(self.frame_scan, text="BLE Scan", command=self.loop.do_scan_tasks)
        self.scan_stop_btn = Button(self.frame_scan, text="BLE Scan Stop", command=self.loop.ble_scan_stop)
        self.connect_btn = Button(self.frame_scan, text="BLE Connect", command=self.loop.do_ble_connect_tasks)
        self.frame = Frame(self.frame_scan)
        self.scrollbar = Scrollbar(self.frame, orient="vertical")
        self.devicelistbox = Listbox(self.frame, selectmode='extended', yscrollcommand=self.scrollbar.set, height=0)
        
        # # -----------------------------------------------------------------------------------------
        self.frame_connect = Frame(self.root)
        self.frame_connect.pack(side="right", fill="both", expand=True)
        self.close_btn = Button(self.frame_connect, text="BLE Disconnect")

        self.measure_btn = Button(self.frame_connect, text="Measure Start")
        self.stop_btn = Button(self.frame_connect, text="Measure Stop")
        self.get_hr_btn = Button(self.frame_connect, text="GET HR")
        self.get_spo2_btn = Button(self.frame_connect, text="GET SPO2")

        self.random_btn = Button(self.frame_connect, text="Random Data")
        
        self.read_text = StringVar()
        self.read_text.set("READ DATA : ")

        self.write_text = StringVar()
        self.write_text.set("READ DATA : ")   

        self.write_label=Label(self.frame_connect, textvariable=self.write_text)
        self.read_label=Label(self.frame_connect, textvariable=self.read_text)

        self.client_frame = Frame(self.frame_connect)
        self.client_scrollbar = Scrollbar(self.client_frame, orient="vertical")
        self.client_listbox = Listbox(self.client_frame, selectmode='extended', yscrollcommand=self.scrollbar.set, height=0)
        
        self.label=Label(self.frame_connect, text="Packet Input ex) 0x02 0x01 0x01 0x01 0x03")
        
        self.text=Text(self.frame_connect)
        self.submit_btn = Button(self.frame_connect, text="Submit")



        self.loop.root_connect(self)

    def run(self):
        # self.change_ui(False)
        self.root.mainloop()

    def before_connect_show(self):

        self.scan_btn.grid(row=1, column=0, sticky=constants.W)
        self.scan_stop_btn.grid(row=1, column=1, sticky=constants.W)
        self.connect_btn.grid(row=1, column=2, sticky=constants.W)
        self.frame.grid(row=2, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.devicelistbox.pack(expand=True, fill=constants.Y)


    def before_connect_hide(self):

        self.scan_btn.grid(row=1, column=0, sticky=constants.W)
        self.scan_stop_btn.grid(row=1, column=1, sticky=constants.W)
        self.connect_btn.grid(row=1, column=2, sticky=constants.W)
        self.frame.grid(row=2, column=0, columnspan=3, sticky=constants.W+constants.E+constants.N+constants.S )
        self.scrollbar.pack(side=constants.RIGHT, fill=constants.Y)
        self.devicelistbox.pack(expand=True, fill=constants.Y)
        
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
        
    def change_ui(self, is_connected):
        if is_connected:
            self.before_connect_hide()
            self.after_connect_show()
        else :
            self.after_connect_hide()
            self.before_connect_show()
            

    def status_label_set(self, messeage):
        self.status_text.set(messeage)

    def read_label_set(self, data):
        self.read_text.set(f"WRITE DATA : {data}")

    def write_label_set(self, data):
        self.write_text.set(f"READ DATA : {data}")

    def devicelistbox_init(self):
        self.devicelistbox.delete(0, constants.END)

    def devicelist_insert(self, num, info):
        self.devicelistbox.insert(num, info)

    def devicelistbox_return(self):
        for i in self.devicelistbox.curselection():
            return self.devicelistbox.get(i).split(' ')[1]
        return None
my_gui = TkGUI()
my_gui.before_connect_show()
my_gui.after_connect_show()
my_gui.run()
