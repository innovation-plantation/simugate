from tkinter import *
from device import *
def exercise(canvas=None):
    gnd = Ground(300,200,canvas=canvas)
    InputPin(50,50)
    InputPin(50,200)
    OutputPin(300,150)
    Pullup(300,100)
    NPN(200,100)
    NPN(150,150)
    circuit.run()
    gnd.canvas.create_text(200,10,text="Create a NAND gate using the two NPN transistors provided")

if __name__=='__main__':
    exercise()
    mainloop()