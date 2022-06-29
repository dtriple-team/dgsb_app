import file

REQ_START_MEASURE = bytearray([0x02, 0x41, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_STOP_MEASURE = bytearray([0x02, 0x42, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_SPO2 = bytearray([0x02, 0x43, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_HR = bytearray([0x02, 0x44, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_WALK_RUN = bytearray([0x02, 0x45, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_MOTION_FLAG = bytearray([0x02, 0x46, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_ACTIVITY = bytearray([0x02, 0x47, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_BATT =bytearray([0x02, 0x48, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_SCD = bytearray([0x02, 0x49, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_ACC = bytearray([0x02, 0x4a, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_GYRO = bytearray([0x02, 0x4b, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_FALL_DETECT = bytearray([0x02, 0x4c, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_TEMP = bytearray([0x02, 0x4d, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_PRESSURE = bytearray([0x02, 0x4e, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_ALL_DATA = bytearray([0x02, 0x4f, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_GET_MAX32630 = bytearray([0x02, 0x50, 0x5E, 0x01, 0x5E, 0x00, 0x03])
REQ_SET_MAX32630_CMD = 0x11

RESP_MEASURE_START_CMD = "0x81"
RESP_MEASURE_STOP_CMD = "0x82"
RESP_SPO2_CMD = "0x83"
RESP_HR_CMD = "0x84"
RESP_WALK_RUN_CMD = "0x85"
RESP_MOTION_FLAG_CMD = "0x86"
RESP_ACTIVITY_CMD = "0x87"
RESP_BATT_CMD = "0x88"
RESP_SCD_CMD = "0x89"
RESP_ACC_CMD = "0x8a"
RESP_GYRO_CMD = "0x8b"
RESP_FALL_DETECT_CMD = "0x8c"
RESP_TEMP_CMD = "0x8d"
RESP_PRESSURE_CMD = "0x8e"
RESP_ALL_DATA_CMD = "0x8f"
RESP_MAX32630_CMD = "0x90"

read_packet = {}
file_test = False # True -> 파싱한 데이터 파일로 저장
parsinglist = []

def change_signed_type(data, division):
    if data>32768:
        return (data-0x10000)/division
    else : 
        return data/division
    
def ble_read_classify_cmd(cmd, data): # cmd 별로 분류 -> 데이터 받을 때 참고 !
    if cmd == RESP_MEASURE_START_CMD:
        if data[0] == 1:
            return "[BLE RESPONSE] MEASURE START!\n"
        else :
            return None
    elif cmd == RESP_MEASURE_STOP_CMD:
        if data[0] == 1:
            return "[BLE RESPONSE] MEASURE STOP!\n"
           
        else :
            return None
    elif cmd == RESP_SPO2_CMD:
        spo2 = data[0]
        spo2_confidence = data[1]
        return f"[BLE RESPONSE] spo2 = {spo2}%, spo2_confidence = {spo2_confidence}%\n"
        
    elif cmd == RESP_HR_CMD:
        hr = data[0]<<8 | data[1]
        hr_confidence = data[2]
        return f"[BLE RESPONSE] hr = {hr}bpm, hr_confidence = {hr_confidence}%\n"
       
    elif cmd == RESP_WALK_RUN_CMD:
        walk = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
        run = data[4]<<24 | data[5]<<16 | data[6]<<8 | data[7]
        return f"[BLE RESPONSE] walk step = {walk}, run step = {run}\n"
      
    elif cmd == RESP_MOTION_FLAG_CMD:
        motion_flag = data[0]
        return f"[BLE RESPONSE] motion_flag = {motion_flag}\n"
      
    elif cmd == RESP_ACTIVITY_CMD:
        return f"[BLE RESPONSE] activity = {data[0]}\n"
    
    elif cmd == RESP_BATT_CMD:
        return f"[BLE RESPONSE] battery = {data[0]}%\n"
      
    elif cmd == RESP_SCD_CMD:
        scd = data[0]
        return f"[BLE RESPONSE] scd = {scd}\n"
     
    elif cmd == RESP_ACC_CMD:
        acc_x = data[0]<<8 | data[1]
        acc_y = data[2]<<8 | data[3]
        acc_z = data[4]<<8 | data[5]
        return f"[BLE RESPONSE] acc_x = {change_signed_type(acc_x, 1000)}, acc_y = {change_signed_type(acc_y, 1000)}, acc_z = {change_signed_type(acc_z, 1000)}\n"
      
    elif cmd == RESP_GYRO_CMD:
        gyro_x = data[0]<<8 | data[1]
        gyro_y = data[2]<<8 | data[3]
        gyro_z = data[4]<<8 | data[5]
        return f"[BLE RESPONSE] gyro_x = {change_signed_type(gyro_x,100)}, gyro_y = {change_signed_type(gyro_y,100)}, gyro_z = {change_signed_type(gyro_z,100)}\n"
     
    elif cmd == RESP_FALL_DETECT_CMD:
        return f"[BLE RESPONSE] fall_detect = {data[0]}\n"
     
    elif cmd == RESP_TEMP_CMD:
        temp = data[0]<<8 | data[1]
        return f"[BLE RESPONSE] temp = {temp/100}°C\n"
     
    elif cmd == RESP_PRESSURE_CMD:
        pressure = data[0]<<8 | data[1]
        return f"[BLE RESPONSE] pressure = {pressure/100}hPa\n"
     
    elif cmd == RESP_ALL_DATA_CMD:
        spo2 = data[0]
        spo2_confidence = data[1]
        hr = data[2]<<8 | data[3]
        hr_confidence = data[4]
        walk = data[5]<<24 | data[6]<<16 | data[7]<<8 | data[8]
        run = data[9]<<24 | data[10]<<16 | data[11]<<8 | data[12]
        motion_flag = data[13]
        activity = data[14]
        battery = data[15]
        scd = data[16]
        acc_x = data[17]<<8 | data[18]
        acc_y = data[19]<<8 | data[20]
        acc_z = data[21]<<8 | data[22]
        gyro_x = data[23]<<8 | data[24]
        gyro_y = data[25]<<8 | data[26]
        gyro_z = data[27]<<8 | data[28]
        fall_detect = data[29]
        temp = data[30]<<8 | data[31]
        pressure = data[32]<<8 | data[33]
        height = data[34]
        weight = data[35]
        age = data[36]
        gender = data[37]
        return f"[BLE RESPONSE] spo2 = {spo2}%, spo2_confidence = {spo2_confidence}% \n hr = {hr}, hr_confidence = {hr_confidence}% \n walk step = {walk}, run step = {run} \n motion_flag = {motion_flag} \n activity = {activity} \n battery = {battery}% \n scd = {scd} \n acc_x = {change_signed_type(acc_x,1000)}, acc_y = {change_signed_type(acc_y,1000)}, acc_z = {change_signed_type(acc_z,1000)} \n gyro_x = {change_signed_type(gyro_x,100)}, gyro_y = {change_signed_type(gyro_y,100)}, gyro_z = {change_signed_type(gyro_z,100)} \n fall_detect = {fall_detect} \n temp = {temp/100}°C \n pressure = {pressure/100}hPa \n height = {height}, weight = {weight}, age = {age}, gender = {gender}\n"
     
    elif cmd == RESP_MAX32630_CMD:
        height = data[0]
        weight = data[1]
        age = data[2]
        gender = data[3]
        return f"[BLE RESPONSE] height = {height}, weight = {weight}, age = {age}, gender = {gender}\n"
    
    return None
def ble_read_parsing(read): # 데이터 parsing 하는 부분
    global read_packet, file_test, parsinglist
    if read['address'] not in read_packet:
        read_packet[read['address']] = []
    for i in list(read['data']): # 하나 씩 체크
        error = False
        if not read_packet[read['address']] and i==2 : # stx 체크
            read_packet[read['address']].append(i)
        elif len(read_packet[read['address']]) == 1 and (i>=129 and i<=146) : # cmd 체크
            read_packet[read['address']].append(i)
        elif (len(read_packet[read['address']]) == 2 or len(read_packet[read['address']]) == 4) and i == 94: # 구분자 체크
            read_packet[read['address']].append(i)
        elif len(read_packet[read['address']])==3: # length 값 받기
            read_packet[read['address']].append(i)
        else :
            if len(read_packet[read['address']])>=5 : # data 받는 영역
                read_packet[read['address']].append(i) 
                if len(read_packet[read['address']]) == read_packet[read['address']][3]+6 : # 총 length와 read data로 온 length를 비교
                    if i == 3: # etx 체크
                        parsinglist.append({'address':read['address'], 'data': read_packet[read['address']]}) # 정상적으로 온 read packet 담기
                        resp_data = ble_read_classify_cmd(hex(read_packet[read['address']][1]), read_packet[read['address']][5:len(read_packet[read['address']])-1])
                        if resp_data :
                            print(resp_data)
                            if file_test:
                                parsingFile = file.File()
                                parsingFile.filename_change(read['name'])
                                parsingFile.file_write_data(resp_data)
                        read_packet[read['address']] = []
                    else: # etx가 아닌 경우 error
                        error = True
            else : # stx, cmd, 구분자 오류인 경우 error
                error = True
        if error :
            print("[BLE READ] ERROR PACKET")
            read_packet[read['address']] = []
    del read_packet[read['address']]