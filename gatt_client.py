import binascii
from bluepy import btle
from time import sleep


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

while(1):
    CharacteristicA = ServiceA.getCharacteristics(0xFF01)[0]
    val = CharacteristicA.read()
    print(val)
    CharacteristicB = ServiceB.getCharacteristics(0xEE01)[0]
    CharacteristicB.write(bytes("Acknowledge", "utf-8"))
