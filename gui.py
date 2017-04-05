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


    # Menu Definitions

    menu = tkinter.Menu(tk)     # menu Main

    # File Menu
    m_file = tkinter.Menu(tk)   # dropdown File

    m_file.add_command(label='Save as...', command=save.saveas)
    m_file.add_command(label='Load', command=save.load)
    #m_file.add_command(label='Dump and Dup', command=save.dump) # for quick testing of save and reload
    m_file.add_command(label='Quit', command=tk.quit)

    # I/O
    m_io = tkinter.Menu(tk)     # dropdown I/O
    for item in [
        ('Input Pin', device.InputPin),
        ('Output Pin', device.OutputPin),
        ('Clock', device.Clock),
        ('Character Display',device.CharDisplay),
    ]:
        m_io.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Components
    m_comp = tkinter.Menu(tk)   # dropdown logic Components
    for item in [
        # transistors and diode
        ('NPN Transistor', device.NPN),
        ('PNP Transistor', device.PNP),
        ('Diode', device.Diode),
        # bus
        ('Bus', device.Bus),
        # weak
        ('Pull-up Resistor Pack', device.PullupPack),  # for use with OC bus
        ('Pull-up Resistor', device.Pullup),
        ('Pull-down Resistor', device.Pulldown),
        # strong
        ('Direct voltage source', device.Source),
        ('Logic ground', device.Ground),
    ]:
        m_comp.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Gates
    m_gate = tkinter.Menu(tk)   # dropdown Logic Gates
    # for the record the inconsistency here kinda bothers me
    # OC gates are defaulted to inverted, but can still be swapped
    # "normal" gates are defaulted to non inverted but can still be swapped
    # it would look nicer if everything was similar to start with
    # like "nand gate" and "nand gate (OC)"
    for item in [
        ('NOT gate', device.Not),
        ('3-state buffer', device.Tri),
        ('AND gate', device.And),
        ('OR gate', device.Or),
        ('XOR gate', device.Xor),
        ('Buffer (Open Collector)', device.OCBuf),
        ('NAND gate (Open Collector)', device.OCNand),
        ('NOR gate (Open Collector)', device.OCNor),
    ]:
        m_gate.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Advanced
    m_adva = tkinter.Menu(tk)   # dropdown Logic Advanced
    for item in [
        ('3-state Driver', device.Driver),
        ('Driver (Open Collector)', device.OCDriver),
        ('Decoder', device.Decoder),
        ('Mux', device.Mux),
        ('DMux', device.DMux),
        ('Adder', device.Adder),
        ('ALU', device.ALU),
    ]:
        m_adva.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Storage
    m_stor = tkinter.Menu(tk)   # dropdown Storage
    for item in [
        # single
        ('SR Flip-Flop (Level-triggered)', device.SR_flipflop),
        ('D Flip-Flop (Level-triggered)', device.D_flipflop),
        ('D Flip-Flop (Edge-triggered)', device.D_edge),
        # group
        ('Latch', device.Latch),
        ('Counter', device.Counter),
        ('Memory', device.Mem),
        ('ROM', device.ROM),
        # group OC
        ('Latch (Open Collector)', device.OCLatch),
        ('Memory (Open Collector)', device.OCMem),
        ('ROM (Open Collector)', device.OCROM),
    ]:
        m_stor.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # add the dropdowns and items to the menu
    menu.add_cascade(label="File", menu=m_file)
    menu.add_cascade(label="I/O Components", menu=m_io)
    menu.add_cascade(label="Discrete Components, Bus and Logic levels", menu=m_comp)
    menu.add_cascade(label="Logic Gates", menu=m_gate)
    menu.add_cascade(label="Drivers and Combinatorial Logic", menu=m_adva)
    menu.add_cascade(label="Storage Devices", menu=m_stor)

    # View commands
    menu.add_command(label='Zoom in', command=zoom_in)
    menu.add_command(label='Zoom out', command=zoom_out)

    # add the full menu to the canvas and run
    tk.config(menu=menu)
    circuit.run()

if __name__=='__main__':
    do_gui()
    tkinter.mainloop()
