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

RESP_ERROR_CMD = "0x80"
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

read_packet = []
def change_signed_type(data, division):
    if data>32768:
        return (data-0x10000)/division
    else : 
        return data/division
    
def ble_read_classify_cmd(cmd, data):
    if cmd == RESP_ERROR_CMD:
        print("[BLE RESPONSE] WRITE PACKET ERROR!\n")
    elif cmd == RESP_MEASURE_START_CMD:
        print("[BLE RESPONSE] MEASURE START!\n")
    elif cmd == RESP_MEASURE_STOP_CMD:
        print("[BLE RESPONSE] MEASURE STOP!\n")
    elif cmd == RESP_SPO2_CMD:
        spo2 = data[0]<<8 | data[1]
        spo2_confidence = data[2]
        print(f"[BLE RESPONSE] spo2 = {spo2}, spo2_confidence = {spo2_confidence}\n")

    elif cmd == RESP_HR_CMD:
        hr = data[0]<<8 | data[1]
        hr_confidence = data[2]
        print(f"[BLE RESPONSE] hr = {hr}, hr_confidence = {hr_confidence}\n")

    elif cmd == RESP_WALK_RUN_CMD:
        walk = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
        run = data[4]<<24 | data[5]<<16 | data[6]<<8 | data[7]
        print(f"[BLE RESPONSE] walk step = {walk}, run step = {run}\n")

    elif cmd == RESP_MOTION_FLAG_CMD:
        motion_flag = data[0]
        print(f"[BLE RESPONSE] motion_flag = {motion_flag}\n")

    elif cmd == RESP_ACTIVITY_CMD:
        print(f"[BLE RESPONSE] activity = {data[0]}\n")

    elif cmd == RESP_BATT_CMD:
        print(f"[BLE RESPONSE] battery = {data[0]}\n")

    elif cmd == RESP_SCD_CMD:
        scd = data[0]
        print(f"[BLE RESPONSE] scd = {scd}\n")

    elif cmd == RESP_ACC_CMD:
        acc_x = data[0]<<8 | data[1]
        acc_y = data[2]<<8 | data[3]
        acc_z = data[4]<<8 | data[5]
        print(f"[BLE RESPONSE] acc_x = {change_signed_type(acc_x, 1000)}, acc_y = {change_signed_type(acc_y, 1000)}, acc_z = {change_signed_type(acc_z, 1000)}\n")

    elif cmd == RESP_GYRO_CMD:
        gyro_x = data[0]<<8 | data[1]
        gyro_y = data[2]<<8 | data[3]
        gyro_z = data[4]<<8 | data[5]
        print(f"[BLE RESPONSE] gyro_x = {change_signed_type(gyro_x,100)}, gyro_y = {change_signed_type(gyro_y,100)}, gyro_z = {change_signed_type(gyro_z,100)}\n")

    elif cmd == RESP_FALL_DETECT_CMD:
        print(f"[BLE RESPONSE] fall_detect = {data[0]}\n")
        
    elif cmd == RESP_TEMP_CMD:
        temp = data[0]<<8 | data[1]
        print(f"[BLE RESPONSE] temp = {temp/100}\n")
        
    elif cmd == RESP_PRESSURE_CMD:
        pressure = data[0]<<8 | data[1]
        print(f"[BLE RESPONSE] pressure = {pressure/100}\n")
        
    elif cmd == RESP_ALL_DATA_CMD:
        spo2 = data[0]<<8 | data[1]
        spo2_confidence = data[2]
        hr = data[3]<<8 | data[4]
        hr_confidence = data[5]
        walk = data[6]<<24 | data[7]<<16 | data[8]<<8 | data[9]
        run = data[10]<<24 | data[11]<<16 | data[12]<<8 | data[13]
        motion_flag = data[14]
        activity = data[15]
        battery = data[16]
        scd = data[17]
        acc_x = data[18]<<8 | data[19]
        acc_y = data[20]<<8 | data[21]
        acc_z = data[22]<<8 | data[23]
        gyro_x = data[24]<<8 | data[25]
        gyro_y = data[26]<<8 | data[27]
        gyro_z = data[28]<<8 | data[29]
        fall_detect = data[30]
        temp = data[31]<<8 | data[32]
        pressure = data[33]<<8 | data[34]
        height = data[35]
        weight = data[36]
        age = data[37]
        gender = data[38]
        print(f"[BLE RESPONSE] spo2 = {spo2}, spo2_confidence = {spo2_confidence} \n hr = {hr}, hr_confidence = {hr_confidence} \n walk step = {walk}, run step = {run} \n motion_flag = {motion_flag} \n activity = {activity} \n battery = {battery} \n scd = {scd} \n acc_x = {change_signed_type(acc_x,1000)}, acc_y = {change_signed_type(acc_y,1000)}, acc_z = {change_signed_type(acc_z,1000)} \n gyro_x = {change_signed_type(gyro_x,100)}, gyro_y = {change_signed_type(gyro_y,100)}, gyro_z = {change_signed_type(gyro_z,100)} \n fall_detect = {fall_detect} \n temp = {temp/100} \n pressure = {pressure/100} \n height = {height}, weight = {weight}, age = {age}, gender = {gender}\n")
            
    elif cmd == RESP_MAX32630_CMD:
        height = data[0]
        weight = data[1]
        age = data[2]
        gender = data[3]
        print(f"[BLE RESPONSE] height = {height}, weight = {weight}, age = {age}, gender = {gender}\n")

def ble_read_parsing(data):
    global read_packet
    for i in list(data):
        if not read_packet :
            if i==2:
                read_packet.append(i)
            else :
                print("[BLE READ] ERROR PACKET")
                read_packet = []
        elif len(read_packet) == 1 :
            if i>=128 and i<=146:
                read_packet.append(i)
            else : 
                print("[BLE READ] ERROR PACKET")
                read_packet = []
        elif len(read_packet) == 2 or len(read_packet) == 4:
            if i == 94:
                read_packet.append(i)
            else :
                print("[BLE READ] ERROR PACKET")
                read_packet = []
        else :
            read_packet.append(i)
            if len(read_packet)>=4 and len(read_packet) == read_packet[3]+6:
                if i==3:
                    ble_read_classify_cmd(hex(read_packet[1]), read_packet[5:len(read_packet)-1])
                else:
                    print("[BLE READ] ERROR PACKET")
                read_packet = []