from tkinter import *
from device import *

def exercise():
    a = Or(200, 100)
    b = Or(200, 200)
    a.o.inverted = b.o.inverted = True
    InputPin(50, 100)
    InputPin(50, 200)
    OutputPin(300, 150)
    circuit.run()
    a.canvas.create_text(200, 10, text="Create a flip flop using the two NOR gates provided")

if __name__=='__main__':
    exercise()
    mainloop()