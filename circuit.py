import functools
import math
import re
import tkinter

import autonum
import logic
import netlist

debug = False
log = print if debug else lambda *x: None


class Item:
    '''An object that has an id, and a type (both are strings).
    A list of all items of each type is maintained.'''
    instances = {}

    @staticmethod
    def get(id, type=None):
        if not type: type = id
        if type not in Item.instances: return None
        items = [item for item in Item.instances[type] if item.id == id]
        return items[0] if len(items) else None

    @classmethod  # so Foo.get_all() will call Item.get_all(Foo) for Foo subclass of Item
    def get_all(typename):
        if type(typename) is type: typename = typename.__name__
        result = Item.instances[typename] if typename in Item.instances else []
        return result

    def __init__(self):
        typename = type(self).__name__
        self.id = autonum.get(typename)
        self.typename = autonum.rootword(typename)
        if self.typename not in Item.instances: Item.instances[self.typename] = []
        Item.instances[self.typename].append(self)
        log('created', self.id)

    def remove(self):
        Item.instances[self.typename].remove(self)
        autonum.delete(self.id)
        log('deleted', self.id)

    def __repr__(self):
        return self.id


class Figure(Item):
    '''
    A Part or a Pin, etc.
    Has an xy location, a shape, and a group associated with its id that all its children belong to.
    '''
    default_canvas = None

    @property
    def xy(self):
        '''complex location value'''
        return self.canvas.coords(self.pivot)

    @xy.setter
    def xy(self, xy):
        old = self.canvas.coords(self.pivot)
        self.canvas.move(self.group, xy[0] - old[0], xy[1] - old[1])

    @property
    def parent(self):
        return self.parent_

    @parent.setter
    def parent(self, parent):
        if self.parent_ is not None:
            self.parent_.children.remove(self)
            self.dtag(self.group, parent.group)
        if parent is not None:
            parent.children.append(self)
            self.canvas.addtag_withtag(parent.group, self.group)
        self.parent_ = parent

    def get_root(self):
        return self.parent_.get_root() if self.parent_ else self

    def __init__(self, x=0, y=0, parent=None, canvas=None, scale=(1, 1),
                 coords=(-10, -10, 10, -10, 10, 10, -10, 10, -10, -10),
                 fill='white',
                 outline='black',
                 width=2,
                 **kwargs
                 ):

        super().__init__()
        self.parent_ = None
        self.children = []
        self.group = '%s_group' % self.id
        self.pivot = '%s_pivot' % self.id
        self.shape = '%s_shape' % self.id
        self.x100 = '%s_x100' % self.id
        self.y100 = '%s_y100' % self.id
        if canvas is None:
            root = self.get_root()
            if root is not self:
                canvas = self.get_root().canvas  # inherit unspecified gui from root
            if canvas is None:
                canvas = Figure.default_canvas  # if it's still unspecified, use previous
                if canvas is None:
                    canvas = tkinter.Canvas(tkinter.Tk())  # if none was ever specified, create a new toolkit
                    canvas.pack()
        self.canvas = canvas
        Figure.default_canvas = self.canvas

        canvas.create_bitmap(0, 0, tags=(self.pivot, self.group), bitmap='gray12',
                             state=tkinter.DISABLED if debug else tkinter.HIDDEN)
        canvas.create_bitmap(100, 0, tags=(self.x100, self.group), bitmap='gray12',
                             state=tkinter.DISABLED if debug else tkinter.HIDDEN)
        canvas.create_bitmap(0, 100, tags=(self.y100, self.group), bitmap='gray12',
                             state=tkinter.DISABLED if debug else tkinter.HIDDEN)
        scaled_coords = [coords[i] * scale[i & 1] for i in range(len(coords))]
        canvas.create_polygon(scaled_coords, tags=(self.shape, self.group), fill=fill, outline=outline, width=width,
                              **kwargs)
        for child in self.children:
            canvas.addtag_withtag(self.group, child.id)
        if parent: x, y = x + parent.x, y + parent.y
        canvas.move(self.group, x, y)
        canvas.update()


class ProtoWire(Item):
    def __init__(self, pin, x, y, canvas=None):
        # self.canvas = canvas if canvas else Figure.default_canvas
        self.pin = pin
        self.canvas = self.pin.canvas
        args = *pin.xy, *pin.gravity, x, y
        self.canvas.create_line(*args, fill='lightyellow', width=2 * logic.width[pin.in_value], smooth=True,
                                tags='proto_wire_bg')
        self.canvas.create_line(*args, fill=logic.color[pin.in_value if pin.out_value == 'Z' else pin.out_value],
                                width=logic.width[pin.in_value], dash=(4, 4), smooth=True, tags='proto_wire_fg')

    def __del__(self):
        self.canvas.delete('proto_wire_fg')
        self.canvas.delete('proto_wire_bg')

    def move(self, x, y):
        for each in 'proto_wire_fg', 'proto_wire_bg':
            coords = self.canvas.coords(each)
            coords[4], coords[5] = x, y
            self.canvas.coords(each, coords)


class Wire(Item):
    '''a segment of a wire from one pin to the next'''
    segments = {}  # sorted(name1, name2) : wire

    @staticmethod
    def operate():
        for group in netlist.groups:
            pins = {pin for segment in group for pin in segment}
            Wire.operate_segments_pins(group, pins)

    @staticmethod
    def operate_segments_pins(group, pins):
        for target_pin in pins:
            other_pins = [pin for pin in pins if pin != target_pin]
            x = map(lambda pin: pin.out_value, other_pins)
            y = functools.reduce(logic.wirefn, x, 'Z')
            target_pin.in_value = y
        x = map(lambda pin: pin.out_value, pins)
        y = functools.reduce(logic.wirefn, x, 'Z')
        for segment in group:
            Wire.segments[segment].reconfig(y)

    @staticmethod
    def wire_reoperate(pins):
        x = map(lambda pin: pin.out_value, pins)
        y = functools.reduce(logic.wirefn, x, 'Z')
        for pin in pins: pin.in_value = y

    def __init__(self, *pins):
        super().__init__()
        self.canvas = pins[0].canvas
        self.pins = tuple(sorted(pins))
        Wire.segments[self.pins] = self
        netlist.connect(*pins)
        value = logic.wirefn(pins[0].in_value, pins[1].in_value)
        self.insulation = self.id + "_insulation"
        self.canvas.create_line(*self.get_coords(), smooth=True,
                                fill='white', width=logic.width[value] + 2,
                                tags=(self.insulation, 'Wire_' + self.pins[0].id, 'Wire_' + self.pins[1].id,))
        self.canvas.create_line(*self.get_coords(), smooth=True,
                                fill=logic.color[value], width=logic.width[value],
                                tags=(self.id, 'Wire_' + self.pins[0].id, 'Wire_' + self.pins[1].id,))

        self.canvas.tag_raise(self.id)
        self.move()  # in case wire needs to be rerouted

    def remove(self):
        ''' Remove the wire from the netlist, from the list of wire segments, and from the wire items pool '''
        netlist.disconnect(*(self.pins))
        Item.remove(self)
        Wire.segments.pop(self.pins)
        return self.id

    def get_coords(self):
        points = (*self.pins[0].xy, *self.pins[0].gravity, *self.pins[1].gravity, *self.pins[1].xy)
        x0, y0, x1, y1, x2, y2, x3, y3 = points
        if self.pins[0].parent is self.pins[1].parent is not None:
            if x1 < x0 < x3 < x2 or x1 > x0 > x3 > x2:
                xx = (x0 + x3) / 2
                yy = (y0 + y3) / 2
                points = x0, y0, x1, y1, xx, yy - 100, x2, y2, x3, y3
            if y1 < y0 < y3 < y2 or y1 > y0 > y3 > y2:
                xx = (x0 + x3) / 2
                yy = (y0 + y3) / 2
                points = x0, y0, x1, y1, xx - 100, yy, x2, y2, x3, y3
        return points

    def move(self):
        self.canvas.coords(self.id, *self.get_coords())
        self.canvas.coords(self.insulation, *self.get_coords())
        self.canvas.tag_raise(self.insulation)
        self.canvas.tag_raise(self.id)
        for pin in self.pins:
            self.canvas.tag_raise(pin.id)

    def reconfig(self, value):
        self.canvas.itemconfig(self.insulation, fill='white', width=logic.width[value] + 2)
        self.canvas.itemconfig(self.id, fill=logic.color[value], width=logic.width[value])

    def __repr__(self):
        return self.id + ': ' + repr(self.pins) + '/' + repr(sorted(netlist.group_of(self.pins[0])))

    def __del__(self):
        self.canvas.delete(self.id)
        self.canvas.delete(self.insulation)


class Inversion(Figure):
    @property
    def inverted(self):
        return self._inverted

    @inverted.setter
    def inverted(self, inverted):
        self._inverted = inverted
        self.canvas.itemconfig(self.shape, fill='white' if inverted else '', outline='black' if inverted else '')
        self.canvas.update()
        if hasattr(self,'inversion_listener') and self.inversion_listener: self.inversion_listener()

    def toggle_inversion(self):
        self.inverted = not self.inverted

    def __init__(self, x, y, canvas=None, invertible=True, inverted=True, inversion_listener=None):
        super().__init__(x, y, canvas=canvas, smooth=True)
        self.inverted = inverted
        self.invertable = invertible
        if invertible:
            self.canvas.tag_bind(self.shape, '<Button-1>', lambda event: self.toggle_inversion())
            self.inversion_listener = inversion_listener
        else:
            self.canvas.itemconfig(self.shape, state=tkinter.DISABLED)
            self.canvas.coords(0, 0)
            self.canvas.tag_lower(self.shape)


class Pin(Figure):
    proto = None
    stiffness = 1

    @property
    def oc(self):
        return self._oc if hasattr(self,'_oc') else None
    @oc.setter
    def oc(self,value):
        self._oc = value

    @property
    def inverted(self):
        if self.bubble:
            return self.bubble.inverted
    @inverted.setter
    def inverted(self,value):
        if self.bubble:
            self.bubble.inverted = value

    @property
    def in_value(self):
        return self._in_value if hasattr(self,'_in_value') else 'U'

    @in_value.setter
    def in_value(self, value):
        self._in_value = value
        value = self._in_value
        self.reconfig()

    @property
    def out_value(self):
        return self._out_value

    @out_value.setter
    def out_value(self, value):
        self._out_value = value
        self.canvas.find_withtag(self.group)
        self.reconfig()

    @property
    def gravity(self):
        '''complex location value'''
        return self.canvas.coords(self.magnet)

    @staticmethod
    def adjust(dx, ddx):
        '''extend ddx beyond dx (relative to dx direction)'''
        return dx + math.copysign(ddx, dx * ddx) if dx else 0

    def reconfig(self):
        value = self.out_value if self.out_value != 'Z' else self.in_value
        if hasattr(self,'line'): self.canvas.itemconfig(self.line, fill=logic.color[value], width=logic.width[value])
        self.canvas.itemconfig(self.shape, outline=logic.color[value], fill=logic.color[value],
                               width=logic.width[value])

    def __init__(self, x=0, y=0, dx=0, dy=0, scale=(.4, .4), smooth=True, fill='black',
                 edge_triggered=False, canvas=None, label='', inverted=False, invertible=True, input='Z', output='Z',
                 inversion_listener=None, parent=None, **kwargs):
        self.invertible = invertible
        self.bubble=None
        super().__init__(x, y, canvas=canvas, fill=fill, scale=scale, smooth=smooth, **kwargs)
        self._in_value = 'Z'
        self._out_value = 'Z'
        self._oc = False
        self.line = self.id + '_line'
        self.canvas.create_line(x, y, x + dx, y + dy, tags=(self.group, self.line))
        self._out_value = output
        self._in_value = input
        self.magnet = self.id + '_magnet'

        self.canvas.create_bitmap(x - dx * Pin.stiffness, y - dy * Pin.stiffness, tags=(self.magnet, self.group),
                                  bitmap='gray12',
                                  state=tkinter.DISABLED if debug else tkinter.HIDDEN)

        leg_pt = x + Pin.adjust(dx, -10), y + Pin.adjust(dy, -10)

        self.bubble = Inversion(*leg_pt, inverted=inverted, invertible=invertible,
                                inversion_listener=inversion_listener)
        self.bubble.parent = self;

        text_pt = x + Pin.adjust(dx, 15), y + Pin.adjust(dy, 15)
        self.canvas.create_text(*text_pt, text=label, tags=(self.group, self.id + '_pintext', self.id))
        self.canvas.addtag_withtag(self.id, self.shape)

        edge_pt = x + Pin.adjust(dx, 10), y + Pin.adjust(dy, 10)
        if edge_triggered:
            self.canvas.create_line(x + (dx or -5), y + (dy or -5), *edge_pt, x + (dx or 5), y + (dy or 5),
                                    tags=(self.group, self.id + '_edge'))

        for tag in (self.shape, self.line):
            self.canvas.tag_bind(tag, '<Button-1>', lambda event: self.mouse_down(event))
            self.canvas.tag_bind(tag, '<B1-Motion>', lambda event: self.mouse_move(event))
            self.canvas.tag_bind(tag, '<ButtonRelease-1>', lambda event: self.mouse_up(event))

        if parent:
            self.xy = [parent.xy[0] + x, parent.xy[1] + y]
            self.parent = parent

    def operate_input(self):
        self.out_value = 'Z'
        if self.inverted:
            self.in_value = '0' if self.in_value in '1H' else '1' if self.in_value in '0L' else self.in_value

    def operate_output(self):
        self.in_value = 'Z'
        if self.oc:
            if self.inverted:
                self.out_value = '0' if self.out_value in '1H' else 'Z' if self.out_value in '0L' else self.out_value
            else:
                self.out_value = 'Z' if self.out_value in '1H' else '1' if self.out_value in '0L' else self.out_value
        elif self.inverted:
            self.out_value = '0' if self.out_value in '1H' else '1' if self.out_value in '0L' else self.out_value

    def mouse_down(self, event):
        Pin.proto = ProtoWire(self, event.x, event.y)

    def mouse_move(self, event):
        Pin.proto.move(event.x, event.y)

    def near_regex(self, x, y, regex, dx=50, dy=50):
        finder = re.compile(regex)
        items = self.canvas.find_enclosed(x - dx, y - dy, x + dx, y + dy)
        tags = [tag for item in items for tag in self.canvas.gettags(item) if finder.match(tag)]
        return tags

    def near_pins(self, x, y):
        tags = self.near_regex(x, y, r'Pin_[0-9]+$')
        return [pin for tag in tags for pin in [Item.get(tag, 'Pin')] if pin]

    def mouse_up(self, event):
        pins = self.near_pins(event.x, event.y)
        closest = None
        for pin in pins:
            dist = math.hypot(event.x - pin.xy[0], event.y - pin.xy[1])
            if closest is None or dist < mindist:
                closest = pin
                mindist = dist
        if closest:
            self.route(closest)
        Pin.proto = None

    def get_wire(self, other):
        return Wire.segments.get(tuple(sorted([self, other])))

    def route(self, other):
        '''
        Remove (if exists) otherwise create a direct link to another pin
        Return the id of the link that was created or deleted.
        '''
        if self is other: return
        link = self.get_wire(other)
        if not link: return Wire(self, other).id
        link_id = link.id
        link.remove()
        return link_id

    def remove(self):
        '''
        Remove all wires associated with this pin before removing it from the pin items pool.
        Return its id.
        :return: id of deleted pin
        '''
        for connection in netlist.direct_connections_to(self):
            Wire.remove(Wire.segments[connection])
        Item.remove(self)

        return self.id

    # NEIL Amazon, RYDER Microsoft, TEDDY Google

    def __lt__(self, other):
        return self.id < other.id


def clockwise(a, x=0, y=0): return [w for pair in zip(*(a[::2], a[1::2])) for w in [x + y - pair[1], y + pair[0] - x]]


def flip(a, x=0, y=0): return [w for pair in zip(*(a[::2], a[1::2])) for w in [pair[0], y + y - pair[1]]]

def stretch(a, factor,  x=0, y=0 ): return [w for pair in zip(*(a[::2], a[1::2])) for w in [pair[0], y +  factor*(pair[1]-y)]]

def mirror(a, x=0, y=0): return [w for pair in zip(*(a[::2], a[1::2])) for w in [x + x - pair[0], pair[1]]]


def counter_clockwise(a, x=0, y=0): return [w for pair in zip(*(a[::2], a[1::2])) for w in
                                            [x + pair[1] - y, y + x - pair[0]]]


def inv2x2(m):
    '2x2 matrix inversion'
    a, b, c, d =m
    det = a*d-b*c
    return d*det,-b*det, -c*det, a*det
def mul2x2(m1,m2):
    a,b,c,d = m1
    e,f,g,h = m2
    '2x2 matrix multiplication'
    return a*e+b*g, a*f+b*h, c*e+d*g, c*f+d*h

class Part(Figure):
    allparts = []

    @property
    def oc(self):
        return self._oc
    @oc.setter
    def oc(self,value):
        import tkinter.font
        if not any(item.invertible for item in self.children): value = False
        if self._oc == value: return
        self._oc = value

        name = self.canvas.itemconfig(self.label)['text'][4]
        if value:
            self.oc_text = self.canvas.create_text(*self.xy, text="\n◇" if name else "◇", font=tkinter.font.Font(weight='bold', size=12, underline=1), tags=self.group)
            self.canvas.itemconfig(self.label, text=name.strip()+'\n')
        else:
            self.canvas.delete(self.oc_text)
            if name: self.canvas.itemconfig(self.label,text=name.strip())
        for o in self.children: o.oc = value

    @property
    def orientation(self):
        x100 = list(map(int,self.canvas.coords(self.x100)))
        y100 = list(map(int,self.canvas.coords(self.y100)))
        x,y = list(map(int,self.canvas.coords(self.pivot)))
        return x100[0]-x, x100[1]-y, y100[0]-x, y100[1]-y
    @orientation.setter
    def orientation(self,t):
        a = list(map(lambda x:x/100,t))
        b = inv2x2(map(lambda x:x/100,self.orientation))
        xx,xy,yx,yy = mul2x2(a,b)
        x0,y0 =  self.canvas.coords(self.canvas.find_withtag(self.pivot))
        for item in self.canvas.find_withtag(self.group):
            coords = self.canvas.coords(item)
            for i in range(0,len(coords),2):
                x,y = coords[i]-x0,coords[i+1]-y0
                x,y = xx*x+yx*y, xy*x+yy*y
                coords[i],coords[i+1] = x+x0,y+y0
            self.canvas.coords(item,coords)

    def rename(self, text):
        if self.oc and text:
            self.canvas.itemconfig(self.label, text="%s\n"%text )
            self.canvas.itemconfig(self.oc_text, text="\n◇")
        elif self.oc:
            self.canvas.itemconfig(self.label, text="")
            self.canvas.itemconfig(self.oc_text, text="◇")
        else:
            self.canvas.itemconfig(self.label, text="%s" % text)



    def __init__(self, x=0, y=0, label=None, **kwargs):
        super().__init__(x, y, **kwargs)
        self._oc = False
        self.pins = []
        self.label = '%s_label' % self.id
        if label is None: label = self.id
        self.canvas.create_text(x, y, tags=(self.label, self.group), text=label, state=tkinter.DISABLED)
        self.canvas.tag_bind(self.shape, '<Button-1>', lambda event: self.mouse_pressed(event))
        self.canvas.tag_bind(self.shape, '<B1-Motion>', lambda event: self.mouse_moved(event))
        Part.allparts.append(self)

    def __del__(self):
        Part.allparts.remove(self)

    def add_pin(self, *args, **kwargs):
        if 'label' in kwargs:
            name = str(kwargs['label'])
            invert = name.startswith('-')
            if invert and 'inverted' not in kwargs:
                name = name[1:]
                kwargs['inverted'] = True
            edge = name.startswith('^')
            if edge and 'edge_triggered' not in kwargs:
                name = name[1:]
                kwargs['edge_triggered'] = True
            kwargs['label'] = name
        pin = Pin(*args, **kwargs, parent=self)
        return pin

    def mouse_pressed(self, event):
        self.old_xy = event.x, event.y
        self.canvas.bind('<Key>', lambda event: self.typed(event))
        self.canvas.tag_raise(self.group)
        self.canvas.focus_set()

    def mouse_moved(self, event):
        self.move(event.x - self.old_xy[0], event.y - self.old_xy[1])
        self.old_xy = event.x, event.y

    def typed(self, event):
        log(event.keysym)
        if (event.keysym == "Right"):
            self.rotate_cw()
        elif (event.keysym == "Left"):
            self.rotate_ccw()
        elif (event.keysym == "Up"):
            self.increase()
            self.move_wires()
            self.canvas.update()
        elif (event.keysym == "Down"):
            self.decrease()
            self.move_wires()
            self.canvas.update()
        elif (event.keysym in "oO"):
            self.oc = not self.o
        elif event.keysym in "0Ll1HhXxWwZzUu":
            self.key_level(event.keysym.upper())
        elif event.keysym == "space":
            self.key_level(None)


    def key_level(self,key):
        pass

    def move_wires(self):
        pins = [item for item in self.children if item.typename == 'Pin']
        all_wires = Wire.get_all()
        for wire in all_wires:
            for pin in pins:
                if pin in wire.pins:
                    wire.move()
                    break

    def move(self, dx, dy):
        '''move relative to current position'''
        # if self.gui: self.gui.move(self.id,dx,dy)
        self.canvas.move(self.group, dx, dy)
        self.move_wires()

    def rotate_cw(self):
        if self.canvas:
            x, y = self.canvas.coords(self.pivot)
            for n in self.canvas.find_withtag(self.group):
                self.canvas.coords(n, clockwise(self.canvas.coords(n), x, y))
            self.move_wires()
            self.canvas.update()
        return self

    def rotate_ccw(self):
        if self.canvas:
            x, y = self.canvas.coords(self.pivot)
            for n in self.canvas.find_withtag(self.group):
                self.canvas.coords(n, counter_clockwise(self.canvas.coords(n), x, y))
            self.move_wires()
            self.canvas.update()
        return self

    def mirror(self):
        if self.canvas:
            x, y = self.canvas.coords(self.pivot)
            for n in self.canvas.find_withtag(self.group):
                self.canvas.coords(n, mirror(self.canvas.coords(n), x, y))
            self.move_wires()
            self.canvas.update()
        return self

    def stretch(self,factor):
        if self.canvas:
            x, y = self.canvas.coords(self.pivot)
            for n in self.canvas.find_withtag(self.shape):
                self.canvas.coords(n, stretch(self.canvas.coords(n), factor, x, y))
            self.move_wires()
            self.canvas.update()
        return self

    def flip(self):
        if self.canvas:
            x, y = self.canvas.coords(self.pivot)
            for n in self.canvas.find_withtag(self.group):
                self.canvas.coords(n, flip(self.canvas.coords(n), x, y))
            self.move_wires()
            self.canvas.update()
        return self

    def increase(self):
        log('increase')
        self.mirror()

    def decrease(self):
        log('decrease')
        self.flip()

    def operate(self):
        log(self.id + "does not operate")

    def inversion_change(self):
        '''override in subclass such as GATE where update such as name of part may be needed'''
        pass


def run():
    for pin in Pin.get_all(): pin.operate_input()
    for part in Part.allparts:
        if part.children: part.operate()
    for pin in Pin.get_all(): pin.operate_output()
    Wire.operate()
    Part.default_canvas.update()
    # for diode in device.Diode.get_all():
    #     diode.operate()
    Figure.default_canvas.after(200, run)
    return Part.default_canvas


if __name__ == '__main__':
    tk = tkinter.Tk()
    can = tkinter.Canvas(tk, height='8i',
                         width='10i')
    can.pack()

    p100 = Part(100, 100, canvas=can)
    Part(200, 200)
    p1 = Pin(100 - 80, 70, dx=30);
    p1.parent = p100
    p1.out_value = 'H'
    p1.in_value = 'H'
    p2 = Pin(100 - 80, 90, dx=30);
    p2.parent = p100
    p2.out_value = '0'
    p2.in_value = '0'
    p3 = Pin(100 - 80, 110, dx=30);
    p3.parent = p100
    p3.out_value = 'L'
    p3.in_value = 'L'
    p4 = Pin(100 - 80, 130, dx=30, edge_triggered=True);
    p4.parent = p100
    p4.out_value = '1'
    p4.in_value = '1'
    clk = Pin(100, 100 + 80, dy=-30, edge_triggered=True);
    clk.parent = p100
    o1 = Pin(100 + 80, 100, dx=-30, edge_triggered=True);
    o1.parent = p100
    top = Pin(100, 100 - 80, dy=30, edge_triggered=True);
    top.parent = p100

    print(Pin.get_all())
    p100.canvas.update()

    print(p100.group)
    tkinter.mainloop()
