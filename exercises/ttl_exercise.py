from tkinter import *
from device import *
def exercise(canvas=None):
    gnd = Ground(100,100,canvas=canvas)
    Pullup(50,100)
    Pullup(70,100)
    NPN(300,100)
    NPN(300,200)
    circuit.run()
    gnd.canvas.create_text(200,10,text="Create a NAND gate using the two NPN transistors provided")

if __name__=='__main__':
    exercise()
    mainloop()