# simugate
Python simulation of logic gates, circuits, down to transistor level using std_logic levels

Get the directory and run any of the following python programs: 
* simugate.py  -  main program for designing gates, along with 2 exercises
* gui.py  -  without the two exercises
* exercises.ff_exercise.py  -  create a flip flop using only the parts provided
* exercises.ttl_exercise.py  -  create a gate using transistors

![image](https://cloud.githubusercontent.com/assets/26174810/23583336/f1d245ae-00e5-11e7-9b0f-730906aac996.png)

You need Python to be installed. Python3 works. (with tkinter, which typically is normally bundled with Python) 

I threw this together recently - maybe it will be of use for some students leaning digital systems design or for teaching it. You can simulate using std_logic at the transistor level to show how TTL and CMOS works as well as putting together ALUs and registers, counters, decoders, etc. (no memory or switches or output devices yet). For open collector output, click the part and type 'o'. To invert an input or output, click where the bubble is or should be. To connect wires, just drag between pins. To disconnect, drag along the same path, but you can't delete parts yet.  
