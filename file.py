from datetime import datetime
class File:
    def __init__(self):
        self.fr = None
        self.fw = None 
        self.fa = None
        self.filename = f"./file/ble_log_{self.return_today()}.txt"
    def filename_change(self, filename):
        self.filename = filename

    def file_write(self, title, data):
        self.fw.write(f'[{title}] data = {data}')

    def file_write_time(self, title, data):
        self.fw = open(self.filename, "a")
        self.fw.write(f'[{title}] data = {data} / datetime = {datetime.now()}\n')
        self.fw.close()
        
    def file_write_data(self, data):
        self.fw = open(f"./file/{self.filename}.txt", "a")
        self.fw.write(data)
        self.fw.close()

    def file_write_close(self):
        self.fw.close()
        
    def return_today(self):
        today = str(datetime.now())
        return f"{today[:10]} {today[11:13]}-{today[14:16]}-{today[17:19]}"