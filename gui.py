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
    can = circuit.Figure.default_canvas = tkinter.Canvas(tk, height=tk.winfo_screenheight(),
                                                         width=tk.winfo_screenwidth(), scrollregion=(0, 0, 5000, 5000))
    h = tkinter.Scrollbar(tk, command=can.xview, orient=tkinter.HORIZONTAL);
    h.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    v = tkinter.Scrollbar(tk, command=can.yview);
    v.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    can.pack()

    menu = tkinter.Menu(tk)


    def zoom_in_parts():
        for part in circuit.Part.allparts:
            if part.selected:
                x,y = part.xy
                part.canvas.move(part.group,-x,-y)
                part.canvas.scale(part.group, 0,0, 2,2)
                part.canvas.move(part.group,x,y)
                part.move_wires()

    def zoom_out_parts():
        for part in circuit.Part.allparts:
            if part.selected and abs(part.orientation[0]) +  abs(part.orientation[1]) > 10:
                x, y = part.xy
                part.canvas.move(part.group, -x, -y)
                part.canvas.scale(part.group, 0, 0, .5, .5)
                part.canvas.move(part.group, x, y)
                part.move_wires()

    def zoom_in():
        canvas = circuit.Figure.default_canvas
        canvas.scale(tkinter.ALL, 0,0, 2,2)

    def zoom_out():
        canvas = circuit.Figure.default_canvas
        canvas.scale(tkinter.ALL, 0,0, .5,.5)

    def toggle_open_collector():
        for part in circuit.Part.allparts:
            if part.selected:
                part.oc = not part.oc

    def toggle_pnp_open_collector():
        for part in circuit.Part.allparts:
            if part.selected:
                part.och = not part.och

    # Menu Definitions

    main_menu = tkinter.Menu(tk)     # menu Main

    menu = tkinter.Menu(tk)

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
        ('Character Display',device.CharDisplay),
        ('Keyboard', device.Keyboard),
    ]:
        m_io.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    m_voltage = tkinter.Menu(tk)
    for item in [
        # strong
        ('Direct voltage source', device.Source),
        ('Logic ground', device.Ground),
        # weak
        ('Pull-up Resistor Pack', device.PullupPack),  # for use with OC bus
        ('Pull-up Resistor', device.Pullup),
        ('Pull-down Resistor', device.Pulldown)
    ]:
        m_voltage.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Discrete Components
    m_discrete = tkinter.Menu(tk)   # dropdown discrete Components
    for item in [
        # transistors and diode
        ('NPN Transistor', device.NPN),
        ('PNP Transistor', device.PNP),
        ('Diode', device.Diode),
    ]:
        m_discrete.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Gates
    m_gate = tkinter.Menu(tk)   # dropdown Logic Gates
    # for the record the inconsistency here kinda bothers me
    # OC gates are defaulted to inverted, but can still be swapped
    # "normal" gates are defaulted to non inverted but can still be swapped
    # it would look nicer if everything was similar to start with
    # like "nand gate" and "nand gate (OC)"
    for item in [
        ('Not', device.Not),
        ('And', device.And),
        ('Or', device.Or),
        ('Xor', device.Xor),
    ]:
        m_gate.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    m_ctrl = tkinter.Menu(tk)   # dropdown Timing and Control
    for item in [
        ('Clock', device.Clock),
        ('Counter', device.Counter),
        ('Ring Counter', device.RingCounter),
    ]:
        m_ctrl.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # Bus interface
    m_bus = tkinter.Menu(tk)    # dropdown Bus Interface
    for item in [
        # bus
        ('Bus', device.Bus),
        ('Buffer', device.Buf),
        ('3-state buffer', device.Tri),
        ('Multi-bit driver', device.Driver),
    ]:  m_bus.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))
    for item in [
        ('Toggle NPN open collector', toggle_open_collector),
        ('Toggle PNP open collector (rare)', toggle_pnp_open_collector)
    ]:  m_bus.add_command(label=item[0], command=item[1])

    # Combinatorial logic
    m_adva = tkinter.Menu(tk)   # dropdown Combinatorial logic
    for item in [
        ('Decoder', device.Decoder),
        ('Mux', device.Mux),
        ('DMux', device.DMux),
        ('4-bit Adder', device.Adder),
        ('8-bit ALU', device.ALU8),
    ]:
        m_adva.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))

    # State
    m_stor = tkinter.Menu(tk)   # dropdown State
    for item in [
        # single-bit
        ('SR Flip-Flop (Level-triggered)', device.SR_flipflop),
        ('D Flip-Flop (Level-triggered)', device.D_flipflop),
        ('D Flip-Flop (Edge-triggered)', device.D_edge),
        # multi-bit
        ('Latch', device.Latch),
        ('Register File', device.RegisterFile),
        ('Memory', device.Mem),
        ('ROM', device.ROM),
        ('ROM Progranner', device.Programmer),

    ]:
        m_stor.add_command(label=item[0], command=lambda constructor=item[1]: constructor(*somewhere()))


    # View commands
    m_view = tkinter.Menu(tk)
    for item in [
        ('Zoom in',zoom_in),
        ('Zoom out', zoom_out),
        ('Grow parts', zoom_in_parts),
        ('Shrink parts', zoom_out_parts),
    ]:
        m_view.add_command(label=item[0], command=item[1])


    # add the dropdowns and items to the menu
    main_menu.add_cascade(label="File", menu=m_file)
    main_menu.add_cascade(label="Power", menu=m_voltage)
    main_menu.add_cascade(label="I/O", menu=m_io)
    main_menu.add_cascade(label="Component", menu=menu)
    main_menu.add_cascade(label="Bus Interface", menu=m_bus)
    main_menu.add_cascade(label="View", menu=m_view)
    menu.add_cascade(label="Discrete", menu=m_discrete)
    menu.add_cascade(label="Gate", menu=m_gate)
    menu.add_cascade(label="Timing & Control", menu=m_ctrl)
    menu.add_cascade(label="Combinatorial", menu=m_adva)
    menu.add_cascade(label="State", menu=m_stor)
    main_menu.add_command(label="Label", command=lambda:device.Labeler(*somewhere()))

    # add the full menu to the canvas and run
    tk.config(menu=main_menu)
    circuit.run()

if __name__=='__main__':
    do_gui()
    tkinter.mainloop()
