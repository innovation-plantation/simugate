# Run this script to create and save a ROM with open-collector output.
# Modify the data parameter to specify the desired contents for the ROM.
# If you don't want open collector outputs, just delete the "OC" from "OCROM"
from save import saveas
from device import *
OCROM(data={0x00: [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80], 0x10: "Aloha!"})
saveas()
