from datetime import datetime
import csv, os
class File:
    def __init__(self, name, date):
        self.fr = None
        self.fw = None 
        self.fa = None
        self.filename = f"./files/{name}_{date}.csv"
    def filename_change(self, filename):
        self.filename = filename

    def file_write(self, title, data):
        self.fw.write(f'[{title}] data = {data}')

    def file_write_time(self, title, address, data):
        self.fw = open(self.filename, "a")
        self.fw.write(f'[{title}] address = {address} / data = {data} / datetime = {datetime.now()}\n')
        self.fw.close()
        
    def file_write_data(self, data):
        self.fw = open(f"/files/{self.filename}.txt", "a")
        self.fw.write(data)
        self.fw.close()

    def file_write_csv(self, data):
        data.append(str(datetime.now())[10:19])
        if os.path.isfile(os.path.join(os.getcwd(),self.filename.replace("./","").replace("/","\\"))):

            f = open(self.filename, "a", newline='')
            wr = csv.writer(f)
            wr.writerow(data)
            f.close()
        else :
            f = open(self.filename, "w", newline='')
            wr = csv.writer(f)
            wr.writerow(["spo2", "spo2 confidence", "hr", "hr confidence", "walk", "run", 
        "motion flag", "activity", "battery", "scd", "acc x", "acc y", "acc z", 
        "gyro x", "gyro y", "gyro z", "fall detect", "temp", "pressure", "time"])
            wr.writerow(data)
            f.close()

    def file_write_close(self):
        self.fw.close()
        
    def return_today(self):
        today = str(datetime.now())
        return f"{today[:10]} {today[11:13]}-{today[14:16]}-{today[17:19]}"