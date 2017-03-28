import tkinter

import circuit
import device
import save

default_xy = 0, 0


def somewhere():
    global default_xy
    default_xy = default_xy[0] % 800 + 10, default_xy[1] % 500 + 20
    return default_xy[0] + 100, default_xy[1] + 100

def do_gui():
    tk = tkinter.Tk()
    can = circuit.Figure.default_canvas = tkinter.Canvas(tk, height='800', width='1000',scrollregion=(0,0,5000,5000))
    h = tkinter.Scrollbar(tk, command=can.xview, orient=tkinter.HORIZONTAL);
    h.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    v = tkinter.Scrollbar(tk, command=can.yview);
    v.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    can.pack()

    menu = tkinter.Menu(tk)


    def zoom_in():
        canvas = circuit.Figure.default_canvas
        canvas.scale(tkinter.ALL, 0,0, 2,2)


    def zoom_out():
        canvas = circuit.Figure.default_canvas
        canvas.scale(tkinter.ALL, 0,0, .5,.5)


    for item in [
        ('ALU', device.ALU),
        ('Adder', device.Adder),
        ('Mux', device.Mux),
        ('DMux', device.DMux),
        ('Decoder', device.Decoder),
        ('Counter', device.Counter),
        ('Latch', device.Latch),
        ('Memory', device.Mem),
        ('ROM', device.ROM),
        ('Edge-triggered D Flip-Flop', device.D_edge),
        ('Level-triggered D Flip-Flop', device.D_flipflop),
        ('Level-triggered SR Flip-Flop', device.SR_flipflop),
        ('AND gate', device.And),
        ('OR gate', device.Or),
        ('XOR gate', device.Xor),
        ('NOT gate', device.Not),
        ('3-state gate', device.Tri),
        ('3-state driver',device.Driver),
        ('Clock', device.Clock),
        ('NPN Transistor', device.NPN),
        ('PNP Transistor', device.PNP),
        ('Pull-up Resistor', device.Pullup),
        ('Pull-down Resistor', device.Pulldown),
        ('Direct voltage source', device.Source),
        ('Logic ground', device.Ground),
        ('Diode', device.Diode),
        ('Open Collector NAND gate', device.OCNand),
        ('Open Collector NOR gate', device.OCNor),
        ('Open Collector Buffer', device.OCBuf),
        ('Open Collector Driver', device.OCDriver),
        ('Open Collector Latch', device.OCLatch),
        ('Open Collector Memory', device.OCMem),
        ('Open Collector ROM', device.OCROM),
        ('Input Pin', device.InputPin),
        ('Output Pin', device.OutputPin),
        ('Character Display',device.CharDisplay),
        ('Bus', device.Bus),
        ('Pullup Resistor Pack', device.PullupPack),
    ]:
        menu.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    #menu.add_command(label='Dump and Dup', command=save.dump)
    menu.add_command(label='Save as...', command=save.saveas)
    menu.add_command(label='Load', command=save.load)
    menu.add_command(label='Zoom in', command=zoom_in)
    menu.add_command(label='Zoom out', command=zoom_out)
    tk.config(menu=menu)
    circuit.run()

if __name__=='__main__':
    do_gui()
    tkinter.mainloop()
