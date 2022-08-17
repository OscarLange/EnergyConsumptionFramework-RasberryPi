import binascii
import sys
from bluepy import btle
from time import sleep
from ina219 import INA219, DeviceRangeError
from threading import Thread, Lock

#set mutex
mutex = Lock()

#test parameters
cpu_frequencies = [80, 160, 240]
cpu_utilization = [25, 50, 75, 100]
work_files = ["noop_test.csv", "add_test.csv", "sub_test.csv", "mul_test.csv", "div_test.csv", "addf_test.csv", "subf_test.csv", "mulf_test.csv", "divf_test.csv"]

#determines which config is currently running
config_index = 0
cur_freq_index = 2 
cur_util_index = 3
cur_work_index = 4

#print current configuration
def print_configuration():
    print("Config:" + str(cpu_frequencies[cur_freq_index]) + "," + str(cpu_utilization[cur_util_index]) + "," + str(work_files[cur_work_index]))

#increase configuration
#function switches through different configuration modes
def inc_configuration():
    global cur_work_index, cur_util_index, cur_freq_index, config_index
    if(config_index < int(sys.argv[1])):
        config_index += 1
        return

    config_index = 0

    if cur_work_index < (len(work_files)-1):
        cur_work_index += 1
        return
    
    cur_work_index = 0
    if cur_util_index < (len(cpu_utilization)-1):
        cur_util_index += 1
        return
    
    cur_util_index = 0
    if cur_freq_index < (len(cpu_frequencies)-1):
        cur_freq_index += 1
        return
    
    cur_freq_index = 0


#average out every collected value
def avg_values(stored_values):
    avg_uges, avg_iges, avg_pges, avg_ushunt = 0,0,0,0
    for stored_value in stored_values:
        value_list = stored_value.split(",")
        avg_uges += float(value_list[0])
        avg_iges += float(value_list[1])
        avg_pges += float(value_list[2])
        avg_ushunt += float(value_list[3])
    avg_uges /= len(stored_values)
    avg_iges /= len(stored_values)
    avg_pges /= len(stored_values)
    avg_ushunt /= len(stored_values)
    return str(avg_uges) + "," + str(avg_iges) + "," + str(avg_pges) + "," + str(avg_ushunt)

#read ina values and store in file
def read_ina219():
    global stored_values
    while(not mutex.acquire(False)):
        values = ""
        Uges = ina.voltage() + ina.shunt_voltage()/1000
        values += '{0:0.2f},'.format(Uges)
        values += '{0:0.2f},'.format(ina.current())
        values += '{0:0.2f},'.format(ina.power())
        values += '{0:0.10f}'.format(ina.shunt_voltage())
        stored_values.append(values)
    mutex.release();

#Resistance of Resistor inside INA219
SHUNT_OHM = 0.1
MAX_CURRENT = 0.4

#ina configurations
ina = INA219(SHUNT_OHM, MAX_CURRENT)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

stored_values = []

print("Connecting ...")
dev = btle.Peripheral("78:21:84:78:c8:36")

print("Services...")
for scv in dev.services:
    print(str(scv))

print("Characteristics")
for char in dev.getCharacteristics(startHnd=1, endHnd=0xFFFF, uuid=None):
    print(str(char))

ServiceA = dev.getServiceByUUID(0x00FF)
ServiceB = dev.getServiceByUUID(0x00EE)

last_val = ""
sleep_timer = 3

while(1):
    CharacteristicA = ServiceA.getCharacteristics(0xFF01)[0]
    val = CharacteristicA.read().decode()
    if val != last_val:
        print(val)
        last_val = val
        if "Freq" in val:
            freq_str = str(cpu_frequencies[cur_freq_index])
            CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
            CharacteristicB.write(bytes(freq_str, "utf-8"))
            dev.disconnect()
            sleep(10)
            dev = btle.Peripheral("78:21:84:78:c8:36")
            ServiceA = dev.getServiceByUUID(0x00FF)
            ServiceB = dev.getServiceByUUID(0x00EE)

        if "Work" in val:
            CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
            work_str = str(cur_work_index)
            CharacteristicB.write(bytes(work_str, "utf-8"))
        if "CPU" in val:
            cpu_str = str(cpu_utilization[cur_util_index])
            CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
            CharacteristicB.write(bytes(cpu_str, "utf-8"))
        if "Start" in val:
            CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
            sleep_timer = 10
            mutex.acquire()
            CharacteristicB.write(bytes("Ok", "utf-8"))
            #dont collect values while the work is initializing
            sleep(1)
            #start another thread that reads the GPIO
            t = Thread(target = read_ina219, args = ())
            t.start()
        if "Stop" in val:
            mutex.release()
            t.join()
            CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
            sleep_timer = 3
            if config_index == int(sys.argv[1]):
                if cur_work_index == (len(work_files)-1) and cur_util_index == (len(cpu_utilization)-1):
                    print("Frequency switch")
                    CharacteristicB.write(bytes("2", "utf-8"))
                else:
                    print("Config switch")
                    CharacteristicB.write(bytes("1", "utf-8"))
            else:
                CharacteristicB.write(bytes("0", "utf-8"))
            #avg_value = avg_values(stored_values)
            #write back to file
            print("Writting to =>" + work_files[cur_work_index])
            file_name = "./training/" + work_files[cur_work_index]
            with open(file_name, 'a') as f:
                try:
                    for val in stored_values:
                        f.write(val + "," + str(cpu_frequencies[cur_freq_index])+ "," + str(cpu_utilization[cur_util_index]))
                        f.write("\n")
                except DeviceRangeError as e:
                    print('Current to large!')

            stored_values = []

            inc_configuration()
    print_configuration()
    sleep(sleep_timer)
