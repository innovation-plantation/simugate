# simugate
Python simulation of logic gates, circuits, down to transistor level using IEEE 1164 std_logic levels

Get the directory and run any of the following python programs: 
* simugate.py  -  main program for designing gates, along with 2 exercise windows included in different ways
* gui.py  -  main program without the two exercises
* exercises.ff_exercise.py  -  create a flip flop using only the parts provided
* exercises.ttl_exercise.py  -  create a gate using transistors
Copy whatever exercises you want to make available up to the main folder.

![image](https://cloud.githubusercontent.com/assets/26174810/24330080/d3ef8032-11b2-11e7-836e-2c79d422c18e.png)

You need Python to be installed. Python3 works. (with tkinter, which typically is normally bundled with Python)

I threw this together recently - maybe it will be of use for some students leaning digital systems design or for teaching it.

You can simulate using std_logic at the transistor level to show how TTL and CMOS works as well as putting together ALUs and registers, counters, decoders, etc.

To invert an input or output, click where the bubble is or should be. To connect wires, just drag between pins. To disconnect, drag along the same path,
but you can't copy parts yet except through undocumented Dump & Dup feature.

For open collector output, set the .oc member True. Currently OCBuf, OCLatch, & OCMem have this in their constructors.

Functions of the ALU are subject to change at this point.

The plus key can be used to increase the number of pins on selected gates.

off or pulled down signals are black. On or pulled-up signals are red. Orange indicates unknown.

Type the character while an input pin is selected to set its value to any std_logic value except '-'

0,1,X: Forced signals (force-off, force-on, unknown or contention from both) drawn as heavy lines

L,H,W: Weak signals (pull-down, pull-up, unknown or contention from both) drawn as thin lines

Z: High impedence (floating with no signal) drawn as a thin blue-violet line.

U: "Uninitialized" is bright cyan colored.

Run simugate.py to get a menu with options to do one of several exercises or to open a schematic editor.
