import alu
import circuit
import functools
import logic
import tkinter


def sample(pin):
    return logic.buffn(pin.in_value)  # if not pin.bubble.inverted else logic.notfn(pin.in_value)


def sample_pins(pins):
    result = 0;
    for n in range(len(pins)):
        value = sample(pins[n])
        if value in '1H':
            result |= 1 << n
        elif value not in '0L':
            raise LookupError
    return result


def set_pins(pins, value):
    for n in range(4):
        pins[n].out_value = '1' if value & 1 << n else '0'


triangle = (-40, -40, 40, 0, -40, 40)


class Gate(circuit.Part):
    def __init__(self, *args, label='', coords=triangle, fn=logic.buffn, init='X', inputs=[-2, 2], inverted=False,
                 **kwargs):
        super().__init__(*args, label=label, coords=coords, **kwargs)
        self.i=[]
        self.i = list(map(lambda y: self.add_pin(-65, y * 10, dx=25), inputs))
        self.fn = fn
        self.init = init
        self.o = self.add_pin(x=65, dx=-25, inversion_listener=lambda: self.inversion_change(), inverted=inverted)

    def operate(self):
        if not hasattr(self,'o'): return
        if not self.i: return
        x = map(lambda pin: sample(pin), self.i)
        y = functools.reduce(self.fn, x, self.init)
        self.o.out_value = y

    def inversion_change(self):
        print("Inversion changed")

    def decrease(self):
        n = len(self.i)
        if n>2 and hasattr(self, 'scaled_shape') and not self.i[n-1].has_wires_connected() and max(max(self.orientation),-min(self.orientation))==100:
            # bug workaround: orientation setting fails when scale is not 100%, so don't allow it in that case
            n-=1
            self.i[n].remove()
            self.i.pop(n)
            orient = self.orientation
            self.orientation = 100, 000, 000, 100
            if n == 2:
                self.canvas.move(self.i[1].group, 0, 20)
            else:
                for i in range(n):
                    self.canvas.move(self.i[i].group, 0, 10)
                self.canvas.coords(self.shape, *self.scaled_shape(n))
                self.canvas.coords(self.glow, *self.scaled_shape(n))
                if hasattr(self, 'extra_scaling'): self.extra_scaling(n)
            self.orientation = orient
            self.move_wires()


    def increase(self):
        n = len(self.i)
        if n>1 and hasattr(self, 'scaled_shape') and max(max(self.orientation),-min(self.orientation))==100:
            # bug workaround: orientation setting fails when scale is not 100%, so don't allow it in that case
            orient = self.orientation
            self.orientation = 100,000,000,100
            if n==2:
                self.canvas.move(self.i[1].group, 0, -20)
                self.i.append(self.add_pin(-65, 20, dx=25))
            else:
                for i in range(n):
                    self.canvas.move(self.i[i].group,0,-10)
                self.i.append(self.add_pin(-65, 10*n, dx=25))
                self.canvas.coords(self.shape,*self.scaled_shape(n+1))
                self.canvas.coords(self.glow, *self.scaled_shape(n + 1))
                if hasattr(self,'extra_scaling'): self.extra_scaling(n+1)
            self.orientation = orient
            self.move_wires()

def scaled_and_shape(n,x=0,y=0):
    k = max(40, n * 10)
    return x-40, y-k, x-40, y-k, x, y-k, x, y-k, x+20, y-k, x+40, y-k+20, x+40, y, x+40, y+k-20, x+20, y+k, x, y+k, x, y+k, x-40, y+k, x-40, y+k

and_shape = scaled_and_shape(4)
           # -40, -40, -40, -40, 0, -40, 0, -40, 20, -40, 40, -20, 40, 0, 40, 20, 20, 40, 0, 40, 0, 40, -40, 40, -40, 40,


class And(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='AND', coords=and_shape, fn=logic.andfn, init='1', smooth=True, **kwargs)

    def inversion_change(self):
        self.rename('NAND' if self.o.bubble.inverted else 'AND')

    def scaled_shape(self,n):
        return scaled_and_shape(n,*self.xy)


def scaled_or_shape(n,x=0,y=0):
        k = max(40,n*10)
        return (x-40, y-k+20, x-40, y-k+10, x-50, y-k, x-50, y-k, x-40, y-k, x-20, y-k+1,
         x+10,y-25,
                x+40, y, x+40, y,
         x+10,y+25,
         x-20, y+k-1, x-40, y+k, x-40, y+k, x-50, y+k, x-50, y+k, x-40, y+k-10, x-40, y+k-20)
or_shape = scaled_or_shape(4)

class Or(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='OR', coords=or_shape, fn=logic.orfn, init='0', smooth=True, **kwargs)

    def inversion_change(self):
        self.rename('NOR' if self.o.bubble.inverted else 'OR')

    def scaled_shape(self,n):
        return scaled_or_shape(n,*self.xy)

class Xor(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='XOR', coords=or_shape, fn=logic.xorfn, init='0', smooth=True, **kwargs)
        x, y = self.xy
        self.xor_tail = self.id+"_tail"
        self.canvas.create_line(*self.scaled_tail(2), smooth=True, fill='black', width=5, state='disabled', tags=(self.group,self.xor_tail))

    def scaled_tail(self, n):
        x, y = self.xy
        k = max(40,n*10)
        return x - 60, y - k, x - 60, y - k+2, x - 50, y - k+10, x - 50, y + k-10, x - 60, y + k-2, x - 60, y + k

    def scaled_shape(self,n):
        return scaled_or_shape(n,*self.xy)

    #this could be improved...
    def extra_scaling(self,n):
        x, y = self.xy
        self.canvas.coords(self.xor_tail, *self.scaled_tail(n))

    def inversion_change(self):
        self.rename('XNOR' if self.o.bubble.inverted else 'XOR')


class Not(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='NOT', fn=logic.orfn, init='0', inputs=[0], inverted=True, **kwargs)

    def inversion_change(self):
        self.rename('NOT' if self.o.bubble.inverted else '')


class Tri(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, inputs=[0], **kwargs)
        self.e = self.add_pin(x=0, y=45, dy=-25)

    def operate(self):
        if not hasattr(self,'e'): return
        i = sample(self.i[0])
        e = sample(self.e)
        self.o.out_value = i if e == '1' else 'Z' if e == '0' else 'X'


diag_diode_shape = (2, 2, 6, -2, 8, 0, 0, 8, -2, 6, 2, 2, -8, 0, 0, -8)
diode_shape = (4, 0, 4, 6, 7, 6, 7, -6, 4, -6, 4, 0, -7, 6, -7, -6)  # 0, 8, -2, 6, 2, 2, -8, 0, 0, -8)


class Diode(circuit.Part):
    def __init__(self, *args, diag=False, **kwargs):
        super().__init__(*args, label='', coords=diag_diode_shape if diag else diode_shape, fill='brown', **kwargs)
        if diag:
            self.a = self.add_pin(-15, -15, dx=10, dy=10, invertible=False)  # annode
            self.c = self.add_pin(15, 15, dx=-10, dy=-10, invertible=False)  # cathode
        else:
            self.a = self.add_pin(-20, 0, dx=12, invertible=False)  # annode
            self.c = self.add_pin(20, 0, dx=-12, invertible=False)  # cathode

    def operate(self):
        if not hasattr(self,'c'): return
        a = logic.dianfn(self.a.in_value, self.c.in_value)
        c = logic.dicafn(self.a.in_value, self.c.in_value)
        self.a.out_value = a
        self.c.out_value = c


class Pullup(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(-10, -60, 10, -70), width=7, outline=logic.color['H'], **kwargs)
        x, y = self.xy
        self.canvas.create_line(x + 0, y - 20, x - 5, y - 25, x + 5, y - 30, x - 5, y - 35, x + 5, y - 40, x - 5,
                                y - 45, x + 5, y - 50, x + 0, y - 55, x + 0, y - 65, width=3, fill=logic.color['H'],
                                tags=(self.group, self.shape))
        self.o = self.add_pin(0, 0, dy=-20, invertible=False)

    def operate(self):
        self.o.out_value = 'H'

class PullupPack(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(-10, -60, 10, -70), width=7, outline=logic.color['H'], **kwargs)
        x0, y0 = self.xy
        y=y0+15
        for x in x0-30, x0-10, x0+10, x0+30:
            self.canvas.create_line(x + 0, y - 20, x - 5, y - 25, x + 5, y - 30, x - 5, y - 35, x + 5, y - 40, x - 5,
                                y - 45, x + 5, y - 50, x + 0, y - 55, x + 0, y - 65, width=3, fill=logic.color['H'],
                                tags=(self.group, self.shape))
        self.o = [self.add_pin(x, 0, invertible=False) for x in (-30,-10,10,30)]
        self.canvas.create_line(x0-30,y-65,x0+30,y-65, width=3, fill=logic.color['H'],
                                tags=(self.group, self.shape))

        self.canvas.create_line(x0, y - 65, x0, y - 80, width=3, fill=logic.color['H'],
                            tags=(self.group, self.shape))

    def operate(self):
        for pin in self.o: pin.out_value = 'H'




class Pulldown(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(-10, 65, 10, 65, 0, 75), fill=logic.color['0'], **kwargs)
        x, y = self.xy
        self.canvas.create_line(x + 0, y + 20, x - 5, y + 25, x + 5, y + 30, x - 5, y + 35, x + 5, y + 40, x - 5,
                                y + 45, x + 5, y + 50, x + 0, y + 55, x + 0, y + 65, width=3, fill=logic.color['L'],
                                tags=(self.group, self.shape))
        self.o = self.add_pin(0, 0, dy=20, invertible=False)

    def operate(self):
        self.o.out_value = 'L'


class Source(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(-10, -15, 10, -25), width=7, outline=logic.color['1'], **kwargs)
        self.o = self.add_pin(0, 0, dy=-20, invertible=False)

    def operate(self):
        self.o.out_value = '1'


class Ground(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(-10, 20, -10, 20, 10, 20, 10, 20, 0, 30, 0, 30),
                         fill=logic.color['0'], **kwargs)
        self.o = self.add_pin(0, 0, dy=20, invertible=False)

    def operate(self):
        self.o.out_value = '0'


class NPN(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(17, 0, -10, 27, -37, 0, -10, -27, 17, 0,), smooth=True, **kwargs)
        x, y = self.xy
        self.btag, self.etag, self.ctag = '%s_B' % self.id, '%s_E' % self.id, '%s_C' % self.id
        self.canvas.create_line(x, y - 15, x - 17, y - 5, width=4, tags=(self.group, self.ctag), state='disabled')  # c
        self.canvas.create_line(x - 17, y + 5, x, y + 15, width=3, tags=(self.group, self.etag), state='disabled',
                                arrow=tkinter.LAST)  # e
        self.canvas.create_line(x - 17, y - 10, x - 17, y + 10, width=6, tags=(self.group, self.btag),
                                state='disabled')  # b
        self.canvas.create_line(x - 70, y, x - 65, y - 5, x - 60, y + 5, x - 55, y - 5, x - 50, y + 5, x - 45, y - 5,
                                x - 40, y + 5, x - 35, y, x - 17, y, width=3,
                                tags=(self.group, self.shape, self.btag))  # r
        self.b = self.add_pin(x=-90, y=0, dx=20, invertible=False)
        self.c = self.add_pin(x=0, y=-35, dy=20, invertible=False)
        self.e = self.add_pin(x=0, y=35, dy=-20, invertible=False)

    def operate(self):
        if not hasattr(self,'e'): return
        self.c.out_value = logic.npnfn(self.e.in_value, self.b.in_value)
        self.canvas.itemconfig(self.btag, fill=logic.color[self.b.in_value])
        self.canvas.itemconfig(self.etag, fill=logic.color[self.e.in_value])
        self.canvas.itemconfig(self.ctag, fill=logic.color[self.c.out_value])


class PNP(circuit.Part):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', coords=(17, 0, -10, 27, -37, 0, -10, -27, 17, 0,), outline=logic.color['H'],
                         smooth=True, **kwargs)
        x, y = self.xy
        self.btag, self.etag, self.ctag = '%s_B' % self.id, '%s_E' % self.id, '%s_C' % self.id
        self.canvas.create_line(x, y - 15, x - 17, y - 5, width=3, tags=(self.group, self.etag), state='disabled',
                                arrow=tkinter.LAST)  # e
        self.canvas.create_line(x - 17, y + 5, x, y + 15, width=4, tags=(self.group, self.ctag), state='disabled')  # c
        self.canvas.create_line(x - 17, y - 10, x - 17, y + 10, width=6, tags=(self.group, self.btag),
                                state='disabled')  # b
        self.canvas.create_line(x - 70, y, x - 65, y - 5, x - 60, y + 5, x - 55, y - 5, x - 50, y + 5, x - 45, y - 5,
                                x - 40, y + 5, x - 35, y, x - 17, y, width=3,
                                tags=(self.group, self.shape, self.btag))  # r
        self.b = self.add_pin(x=-90, y=0, dx=20, invertible=False)
        self.e = self.add_pin(x=0, y=-35, dy=20, invertible=False)
        self.c = self.add_pin(x=0, y=35, dy=-20, invertible=False)

    def operate(self):
        if not hasattr(self,'c'): return
        self.c.out_value = logic.pnpfn(self.e.in_value, self.b.in_value)
        self.canvas.itemconfig(self.btag, fill=logic.color[self.b.in_value])
        self.canvas.itemconfig(self.etag, fill=logic.color[self.e.in_value])
        self.canvas.itemconfig(self.ctag, fill=logic.color[self.c.out_value])


class Box(circuit.Part):
    def __init__(self, *args, width=4, height=4, vpad=2, hpad=1, **kwargs):
        self.width, self.height = 10 * (hpad + width), 10 * (vpad + height)
        self.vpad, self.hpad = vpad, hpad
        coords = -self.width, -self.height, self.width, -self.height, self.width, self.height, -self.width, self.height
        super().__init__(*args, coords=coords, **kwargs)
        self.left_pins, self.bottom_pins, self.right_pins = [], [], []

    def create_pins(self, names, add_pin):
        pins = []
        for n in range(len(names)):
            if names[n] is None: continue
            pins.append(add_pin(names[n], (len(names) * 10) - n * 20 - 10))
        return pins

    def create_left_pin(self, name='', y=0, **kw_args):
        return self.add_pin(-self.width - 25, y, dx=25, label=name, **kw_args)

    def create_right_pin(self, name='', y=0, **kw_args):
        return self.add_pin(self.width + 25, y, dx=-25, label=name, **kw_args)

    def create_bottom_pin(self, name='', x=0, **kw_args):
        return self.add_pin(x, self.height + 25, dy=-25, label=name, **kw_args)

    def create_left_pins(self, names):
        return self.create_pins(names, self.create_left_pin)

    def create_right_pins(self, names):
        return self.create_pins(names, self.create_right_pin)

    def create_bottom_pins(self, names):
        return self.create_pins(names, self.create_bottom_pin)

    def resize_shape(self, width=None, height=None, vpad=None, hpad=None):
        if height is None: height = self.height/10-self.vpad
        if width is None: width = self.width/10-self.hpad
        if vpad is None: vpad = self.vpad
        if hpad is None: hpad = self.hpad
        self.width, self.height = 10 * (hpad + width), 10 * (vpad + height)
        self.vpad, self.hpad = vpad, hpad
        x,y = self.xy
        coords = x-self.width, y-self.height, x+self.width, y-self.height, x+self.width, y+self.height, x-self.width, y+self.height
        self.canvas.coords(self.shape, coords)
        self.canvas.coords(self.glow, coords)

class Decoder(Box):
    def __init__(self, *args, bits=2, **kwargs):
        w, h = bits, 2 ** bits
        super().__init__(*args, width=w, height=h, label='', **kwargs)
        self.i = self.create_bottom_pins(['s%d' % 2 ** n for n in range(w)])
        self.o = self.create_right_pins(([n for n in range(h)]))

    def operate(self):
        if not hasattr(self,'o'): return
        try:
            value = sample_pins(self.i)
            for n in range(len(self.o)): self.o[n].out_value = '1' if n == value else '0'
        except LookupError:
            for n in range(len(self.o)): self.o[n].out_value = 'X'

    def increase(self):
        print("INC")
        n = len(self.i)
        m = len(self.o)
        if n > 1 and max(max(self.orientation), -min(self.orientation)) == 100:
            # bug workaround: orientation setting fails when scale is not 100%, so don't allow it in that case
            orient = self.orientation
            self.orientation = 100, 000, 000, 100
            oldheight = self.height
            oldwidth = self.width
            self.resize_shape(width=n + 1, height=2 ** (n + 1))
            for k in range(n):
                self.canvas.move(self.i[k].group, 10,self.height-oldheight)
            for k in range(m):
                self.canvas.move(self.o[k].group, self.width-oldwidth, 10*m)
            self.i.append(self.create_bottom_pin(name='s%d' % 2 ** n ,x=-10 * n))
            for k in range(m,m+m):
                self.o.append(self.create_right_pin(k,y=20*(m-k)-10))
            self.orientation = orient
            self.move_wires()


class Mux(Box):
    def __init__(self, *args, bits=2, **kwargs):
        w, h = bits, 2 ** bits
        super().__init__(*args, label='MUX', height=h, width=w, **kwargs)
        self.i = self.create_left_pins([n for n in range(h)])
        self.a = self.create_bottom_pins(['s%d' % 2 ** n for n in range(w)])
        self.o = self.create_right_pin()

    def operate(self):
        if not hasattr(self,'a'): return
        try:
            value = sample_pins(self.a)
            self.o.out_value = logic.buffn(self.i[value].in_value)
        except LookupError:
            self.o.out_value = 'X'


class DMux(Box):
    def __init__(self, *args, bits=2, **kwargs):
        w, h = bits, 2 ** bits
        super().__init__(*args, label='DMUX', height=h, width=w, **kwargs)
        self.o = self.create_right_pins([n for n in range(h)])
        self.a = self.create_bottom_pins(['s%d' % 2 ** n for n in range(w)])
        self.i = self.create_left_pin()

    def operate(self):
        if not hasattr(self,'o'):return
        try:
            value = sample_pins(self.a)
            for n in range(len(self.o)): self.o[n].out_value = logic.buffn(self.i.in_value) if n == value else '0'
        except (AttributeError,LookupError):
            for n in range(len(self.o)): self.o[n].out_value = 'X'


class Latch(Box):
    def __init__(self, *args, bits=4, **kwargs):
        w, h = 1, bits
        super().__init__(*args, label='', height=h, width=1, vpad=0, **kwargs)
        self.i = self.create_left_pins(['' for n in range(h)])
        self.o = self.create_right_pins(['' for n in range(h)])
        self.m = ['X'] * h
        self.clk = self.create_bottom_pin('^')
        self.old_clk = 'X'

    def operate(self):
        if not hasattr(self,'clk'): return
        clk = sample(self.clk)
        if self.old_clk == '0' and clk == '1':
            for bit in range(4):
                self.m[bit] = logic.buffn(self.i[bit].in_value)
        self.old_clk = clk
        for bit in range(4):
            self.o[bit].out_value = self.m[bit]


class Mem(Box):
    def __init__(self, *args, abits=8, dbits=8, **kwargs):
        w, h = 2, max(abits,dbits)
        super().__init__(*args, label='', height=h, width=1, vpad=0, **kwargs)
        self.a = self.create_left_pins(['' for n in range(abits)])
        self.d = self.create_right_pins(['' for n in range(dbits)])
        self.m = [['X']*dbits for i in range(1<<abits)]
        self.r,self.clk = self.create_bottom_pins(['R','^W'])
        self.old_clk = 'X'

    def operate(self):
        if not hasattr(self,'clk'): return
        clk = sample(self.clk)
        r = sample(self.r)
        try: addr = sample_pins(self.a)
        except LookupError: addr=0
        if self.old_clk == '0' and clk == '1':
            for bit in range(len(self.d)):
                self.m[addr][bit] = logic.buffn(self.d[bit].in_value)
        self.old_clk = clk
        if (r=='1'):
            for bit in range(len(self.d)):
                self.d[bit].out_value = self.m[addr][bit]
        else:
            for bit in range(len(self.d)):
                self.d[bit].out_value = 'Z'

class ROM(Box):
    '''
    Uses prog_data if it exists, then overwrites with data if it exists.
    If prog_data does not exist, a simple pattern is used with all zeroes in some addresses and all ones in others.
    '''
    @property
    def prog_data(self):
        return ''.join(['%02x'%int(''.join(reversed(d)),2) for d in self.m])
    @prog_data.setter
    def prog_data(self, dump):
        self.m = [ [x for x in reversed('{0:08b}'.format(x))] for x in bytearray.fromhex(dump)]

    def __init__(self, *args, abits=8, dbits=8, prog_data=None,data={0:"Hello, world!"}, **kwargs):
        w, h = 2, max(abits,dbits)
        super().__init__(*args, label='', height=h, width=1, vpad=0, **kwargs)
        self.a = self.create_left_pins(['' for n in range(abits)])
        self.d = self.create_right_pins(['' for n in range(dbits)])

        if prog_data: self.prog_data = prog_data
        else: self.m = [['0' if i&2 else '1']*dbits for i in range(1<<abits)]

        for addr,data in data.items():
            if type(data) is str:
                text = data
                for i in range(len(text)):
                    self.m[addr+i] = ['1' if 1 << bit & ord(text[i]) else '0' for bit in range(8)]
            elif type(data) is int:
                self.m[addr] = ['1' if 1 << bit & data else '0' for bit in range(8)]
            elif type(data) in (list,tuple):
                for i in range(len(data)):
                    self.m[addr+i] = ['1' if 1 << bit & data[i] else '0' for bit in range(8)]
        self.r = self.create_bottom_pin('R')

    def operate(self):
        if not hasattr(self,'r'): return
        r = sample(self.r)
        try: addr = sample_pins(self.a)
        except LookupError: addr=0
        if (r=='1'):
            for bit in range(len(self.d)):
                self.d[bit].out_value = self.m[addr][bit]
        else:
            for bit in range(len(self.d)):
                self.d[bit].out_value = 'Z'



class SR_flipflop(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, height=3, width=2, label='')
        self.s, self.r = self.create_left_pins(['S', None, 'R'])
        self.q2, self.q1 = self.create_right_pins(['-Q', None, 'Q'])
        self.m1, self.m2 = 'X', 'X'

    def operate(self):
        if not hasattr(self,'m2'): return
        s = sample(self.s)
        r = sample(self.r)
        self.m1, self.m2 = logic.norfn(r, self.m2), logic.norfn(s, self.m1)
        self.q1.out_value = self.m1
        self.q2.out_value = logic.notfn(self.m2)


class D_flipflop(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, width=2, height=3, **kwargs, label='')
        self.clk, self.d = self.create_left_pins(['Clk', None, 'D'])
        self.q2, self.q1 = self.create_right_pins(['-Q', None, 'Q'])
        self.m = 'X'

    def operate(self):
        if not hasattr(self,'m'): return
        d, clk = sample(self.d), sample(self.clk)
        self.m = d if clk == '1' or d == self.m else self.m if clk == '0' else 'X'
        self.q1.out_value = self.q2.out_value = self.m


class D_edge(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, width=1, height=2, label='')
        self.clk = self.create_bottom_pin('^')
        self.d = self.create_left_pin('D')
        self.q = self.create_right_pin('')
        self.old_clk = 'X'
        self.m = 'X'

    def operate(self):
        if not hasattr(self,'d'): return
        d = sample(self.d)
        clk = sample(self.clk)
        if self.old_clk == '0' and clk == '1': self.m = d
        self.q.out_value = self.m
        self.old_clk = clk


class Adder(circuit.Part):
    def __init__(self, *args, **kwargs):
        coords = -40, -100, 40, -60, 40, 60, -40, 100, -40, 10, -30, 0, -40, -10
        super().__init__(*args, label='', coords=coords, **kwargs)
        self.a, self.b, self.o = [], [], []
        for bit in range(4):
            self.a.append(self.add_pin(-65, 0 - bit * 20 - 25, dx=25, label='a%d' % bit if bit % 4 == 3 else ''))
            self.b.append(self.add_pin(-65, 110 - bit * 20 - 25, dx=25, label='b%d' % bit if bit % 4 == 3 else ''))
            self.o.append(self.add_pin(65, 90 - bit * 20 - 15 - 25, dx=-25))
        self.c = self.add_pin(65, 90 - 5 * 20 - 15 - 25, dx=-25)

    def operate(self):
        if not hasattr(self,'c'): return
        try:
            a = sample_pins(self.a)
            b = sample_pins(self.b)
            total = a + b
            self.c.out_value = '1' if total & 0x10 else '0'
            set_pins(self.o, total)
        except LookupError:
            self.c.out_value = 'X'
            for n in range(4):
                self.o[n].out_value = 'X'


class ALU(Adder):
    #  16 functions such as ADD SUB ADC SBC  SLC SRC RLC RRC  AND OR XOR NOT  XFER STC CMC CLR
    def __init__(self, *args, width=4, height=4, pad=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = []
        for bit in range(4):
            x = 30 - 20 * bit
            y = 120
            self.f.append(self.add_pin(x, y, dy=-15 - 10 * (4 - bit), label='s%d' % 2 ** bit))
        self.old_c = 'X'

    def operate(self):
        if not hasattr(self,'c'): return
        try:
            try:
                f = sample_pins(self.f)
                txt, argc = alu.alu_info(f)
                self.rename(txt)
            except LookupError:
                self.rename('')
                raise
            a = sample_pins(self.a) if argc > 0 else 0
            b = sample_pins(self.b) if argc > 1 else 0
            r, c = alu.alu_fn(f, a, b, 4)
            set_pins(self.o, r)
            if c is None:
                self.c.out_value = self.old_c
            else:
                self.old_c = self.c.out_value = '1' if c else '0'
        except (AttributeError,LookupError):
            self.c.out_value = 'X'
            for n in range(4):
                self.o[n].out_value = 'X'


class Counter(Box):
    def __init__(self, *args, bits=4, **kwargs):
        w, h = 1, bits
        super().__init__(*args, label='', height=h, width=2, **kwargs)
        self.i = self.create_left_pins(['' for n in range(h)])
        self.o = self.create_right_pins(['' for n in range(h)])
        self.value = -1
        self.rst,self.clk, self.ld = self.create_bottom_pins(['RST','^', 'LD'])
        self.old_clk = 'X'

    def operate(self):
        if not hasattr(self,'clk'): return
        clk = sample(self.clk)
        ld = sample(self.ld)
        rst = sample(self.rst)
        if clk in 'ZXWU':
            self.value = -1
        elif self.old_clk == '0' and clk == '1':
            if ld in 'H1':
                try:
                    self.value = sample_pins(self.i)
                except LookupError:
                    self.value = -1
            elif ld in 'L0':
                if self.value >= 0: self.value += 1
            else:
                self.value = -1
        if rst in 'H1':
            self.value = 0
        if self.value >= 0:
            set_pins(self.o, self.value)
        else:
            for bit in range(4):
                self.o[bit].out_value = 'X'
        self.old_clk = clk


class Clock(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='Clock', height=0, width=1, **kwargs)
        self.o = self.create_right_pin('')
        self.value = '0'
        circuit.Figure.default_canvas.after(1000, lambda: self.tick())

    def tick(self):
        self.value = '1' if self.value == '0' else '0'
        circuit.Figure.default_canvas.after(1000, lambda: self.tick())

    def operate(self):
        if not hasattr(self,'o'): return
        self.o.out_value = self.value


class OCLatch(Latch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oc=True

class OCMem(Mem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oc=True

class OCROM(ROM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oc=True

class OCBuf(Gate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, label='', fn=logic.orfn, init='0', inputs=[0], **kwargs)
        self.oc=True

    def inversion_change(self):
        self.rename('NOT' if self.o.bubble.inverted else '')

class OCNand(And):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oc=True
        self.o.bubble.inverted=True

class OCNor(Or):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oc=True
        self.o.bubble.inverted=True


one_way_coords=(-40,-10, 40,-10, 50,0, 40,10, -40,10)
class OutputPin(circuit.Part):
    def __init__(self, *args, name='OUTPUT=',**kwargs):
        self.name = name
        super().__init__(*args, coords = one_way_coords, **kwargs)
        self.pin = self.add_pin(-60,0, dx=20, invertible=False)

    def operate(self):
            self.rename('%s %s'%(self.name,self.pin.in_value))
            self.canvas.itemconfig(self.shape,outline=logic.color[self.pin.in_value])

class InputPin(circuit.Part):
    def __init__(self, *args, name='INPUT=',**kwargs):
        self.name = name
        super().__init__(*args, coords=one_way_coords, **kwargs)
        self.pin = self.add_pin(70, 0, dx=-20, invertible=False)
        self.value = 'Z'
        self.rename(self.name)

    def operate(self):
        if '=' in self.name: self.rename('%s %s' % (self.name, self.value))
        self.pin.out_value = self.value
        self.canvas.itemconfig(self.shape,outline=logic.color[self.value])

    def key_level(self,key):
        if not key: key= 'H' if self.value == '0' else '0'
        self.value = key

class Driver(Box):
    def __init__(self, *args, bits=4, **kwargs):
        w, h = 1, bits
        super().__init__(*args, label='', height=h, width=1, vpad=0, **kwargs)
        self.i = self.create_left_pins(['' for n in range(h)])
        self.o = self.create_right_pins(['' for n in range(h)])
        self.e = self.create_bottom_pin('EN')

    def operate(self):
        if not hasattr(self,'e'): return
        e = sample(self.e)
        if e=='1':
            for n in range(len(self.o)): self.o[n].out_value = sample(self.i[n])
        else:
            for n in range(len(self.o)): self.o[n].out_value ='Z' if e == '0' else 'X'

class OCDriver(Driver):
     def __init__(self, *args, **kwargs):
         super().__init__(*args,**kwargs)
         self.oc = True

class Bus(circuit.Part):
    def __init__(self, *args,label='', coords=(-2,-40, -2,40, 2,40, 2,-40), **kwargs):
        super().__init__(*args, label=label,coords=coords, **kwargs)
        for y in 30,10,-10,-30: self.add_pin(0,y,invertible=False)



class CharDisplay(Box):
    def __init__(self, *args, bits=7, **kwargs):
        w, h = 3, 7
        super().__init__(*args, label='', height=h-.5, width=w, vpad=0, **kwargs)
        self.i = self.create_left_pins(['' for n in range(h)])
        self.o = self.create_right_pins(['' for n in range(h)])
        self.m = ['X'] * h
        self.clk = self.create_bottom_pin('^')
        self.old_clk = 'X'

    def operate(self):
        if not hasattr(self,'clk'): return
        clk = sample(self.clk)
        if self.old_clk == '0' and clk == '1':
            for bit in range(len(self.m)):
                self.m[bit] = logic.buffn(self.i[bit].in_value)
                ch=0
                for n in range(len(self.m)):
                    if self.m[n] in "1H":
                        ch |= 1<<n
            self.canvas.itemconfig(self.label, font=('tkfixed',72))
            self.rename(chr(ch))
        self.old_clk = clk
        for bit in range(len(self.m)):
            self.o[bit].out_value = self.m[bit]
