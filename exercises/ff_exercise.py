from tkinter import *
from device import *

def exercise():
    a=Or(200,100)
    b=Or(200,200)
    a.o.inverted = b.o.inverted = True
    Pullup(50,100).o.route(Ground(25,100).o)
    Pullup(50,200).o.route(Ground(25,200).o)
    circuit.run()
    a.canvas.create_text(200,10,text="Create a flip flop using the two NOR gates provided")

if __name__=='__main__':
    exercise()
    mainloop()