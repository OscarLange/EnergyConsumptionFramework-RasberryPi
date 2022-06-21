from ina219 import INA219, DeviceRangeError
from time import sleep
import socket
from threading import Thread, Lock

#set mutex
mutex = Lock()

#Acknowledge message 
ack = "Acknowledged";

#Resistance of Resistor inside INA219
SHUNT_OHM = 0.1
MAX_CURRENT = 0.4

#ina configurations
ina = INA219(SHUNT_OHM, MAX_CURRENT)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

stored_values = []
#sanitize_espoutput
def sanitize_output(input):
    return input.decode();

#read ina values and store in file
def read_ina219():
    global stored_values
    while(not mutex.acquire(False)):
        values = ""
        Uges = ina.voltage() + ina.shunt_voltage()/1000
        print('Ubat  : {0:0.2f}V'.format(Uges))
        values += '{0:0.2f},'.format(Uges)
        print('Iges  : {0:0.2f}mA'.format(ina.current()))
        values += '{0:0.2f},'.format(ina.current())
        print('Pges  : {0:0.2f}mW'.format(ina.power()))
        values += '{0:0.2f},'.format(ina.power())
        print('Ushunt  : {0:0.2f}mV\n'.format(ina.shunt_voltage()))
        values += '{0:0.2f}'.format(ina.shunt_voltage())
        print(values)
        stored_values.append(values)
        sleep(1)
    mutex.release();
    
#create socket to listen on
sock = socket.socket();
sock.bind(('0.0.0.0', 8090));
sock.listen(0);

#main loop to wait on incoming msg
while 1:
    client, addr = sock.accept();    
    try:
        while 1:
            content = client.recv(2048);
            if len(content) == 0:
                break;
            else:
                sanitized_content = sanitize_output(content)
                print(sanitized_content);
                if("Start collecting" in sanitized_content):
                    mutex.acquire()
                    #dont collect values while the work is initializing
                    sleep(3)
                    t = Thread(target = read_ina219, args = ())
                    t.start()
                elif ("Stop collecting" in sanitized_content):
                    mutex.release()
                    t.join()
                else:
                    got_entry = ""
                    entries = sanitized_content.split(";")
                    needed_values = ["work_task", "main", "IDLE", "IDLE"]
                    needed_values_2 = ["MIN_FREQ", "MAX_FREQ"]
                    for needed_value in needed_values:
                        for entry in entries:
                            print(needed_value + " , " + entry);
                            if needed_value in entry:
                                appendix = "," + entry.split(",")[1] + "," + entry.split(",")[2]
                                stored_values = [value + appendix for value in stored_values]
                                got_entry = entry
                                break
                    
                    for needed_value in needed_values_2:
                        for entry in entries:
                            print(needed_value + " , " + entry);
                            if needed_value in entry:
                                appendix = "," + entry.split(",")[1]
                                stored_values = [value + appendix for value in stored_values]
                                got_entry = entry
                                break
                    
                        entries.remove(got_entry)
                    for value in stored_values:
                        print(value)
                     
                    with open('add_test.csv', 'a') as f:
                        try:
                            for value in stored_values:
                                print(value)
                                f.write(value)
                                f.write("\n")
                        except DeviceRangeError as e:
                            print('Current to large!')
                    stored_values = []
            client.send(ack.encode());

    except KeyboardInterrupt:                    
        print("Closing connection");
        client.close();
