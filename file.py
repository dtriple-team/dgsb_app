from datetime import datetime
class File:
    def __init__(self):
        self.fr = None
        self.fw = None 
        self.fa = None

    def file_write_init(self, filename):
        self.fw = open(filename, "w")
    def file_write(self, title, data):
        self.fw.write(f'[{title}] data = {data}')
    def file_write_time(self, title, data):
        self.fw.write(f'[{title}] data = {data} / datetime = {datetime.now()}\n')
        self.fw.close()
    def file_write_close(self):
        self.fw.close()