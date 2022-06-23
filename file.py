from datetime import datetime
class File:
    def __init__(self):
        self.fr = None
        self.fw = None 
        self.fa = None
        today = str(datetime.now())
        self.filename = f"ble_log_{today[:10]} {today[11:13]}-{today[14:16]}-{today[17:19]}.txt"
    def file_write_init(self, filename):
        self.filename = filename
    def file_write(self, title, data):
        self.fw.write(f'[{title}] data = {data}')
    def file_write_time(self, title, data):
        self.fw = open(self.filename, "a")
        self.fw.write(f'[{title}] data = {data} / datetime = {datetime.now()}\n')
        self.fw.close()
    def file_write_close(self):
        self.fw.close()
    