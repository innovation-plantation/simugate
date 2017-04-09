import configparser
import io
import re
import tkinter.filedialog

import circuit
import netlist



def write_file(file, selected=False):
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option

    def pinnum(pin):
        return pin.id.rsplit('Pin_')[1]

    def pinlist(part):
        return " ".join([
                            "%s%s" % ('-' if any(inv for inv in pin.children if inv.inverted) else ''
                                      , pinnum(pin))
                            for pin in part.children if "Pin_" in pin.id])


    allparts = [part for part in circuit.Part.allparts if part.selected] if selected else circuit.Part.allparts

    config['PARTS'] = {part:
                           "%d %d : %s" %
                           (round(int(part.xy[0]), 1),
                            round(int(part.xy[1]), 1),
                            pinlist(part))
                       for part in allparts}

    config['OC'] = {part: part.oc_type
                       for part in allparts if part.oc_type}

    config['WIRES'] = {'net_%d' % n:
                           ' '.join([pinnum(pin) for segment in netlist.groups[n] for pin in segment])
                       for n in range(len(netlist.groups))}
    config['ORIENT'] = {part:
                           "%d %d %d %d"%part.orientation
                       for part in allparts if part.orientation != (100,0,0,100) }

    config['PROG'] = {part: part.prog_data
                       for part in allparts if 'prog_data' in dir(part)}

    for section in config.sections():
            if not len(config[section]):
                config.remove_section(section)
    config.write(file)
    return config


def load_from_config(config, dx=0, dy=0):
    ### now read it back in
    re_partname_n = re.compile(r'^\s*(\w+?)(_\d+)?\s*$')
    re_x_y_pins = re.compile(r'^\s*(-?\d+)\s*(-?\d+)\s*:\s*([-\d ]*)\s*$')

    pinmap = {}
    if 'PARTS' not in config:
        print("NO PARTS SECTION IN CONFIG FILE")
        return
    if 'PARTS' in config:
        for partrecord in config['PARTS']:
            found = re_partname_n.findall(partrecord)
            if len(found) < 1:
                print("Failed to process",partrecord, "with re ",re_partname_n.findall)
                continue
            partname, serialnumber = re_partname_n.findall(partrecord)[0]
            s = config['PARTS'][partrecord]
            result = re_x_y_pins.findall(s)
            x, y, pins = result[0]
            x, y = int(x), int(y)
            cmd = 'device.%s(%d,%d)' % (partname, x + dx, y + dy)
            exec('import device')
            try:
                unit = eval(cmd)
                pin_numbers = [int(pinnum) for pinnum in pins.split(' ') if len(pinnum.strip()) > 0]
                pincount = 0
                while len(unit.children) < len(pin_numbers):
                    unit.increase()
                    if len(unit.children) == pincount: break # no growth
                for i in range(len(unit.children)):
                    unit.children[i].bubble.inverted = pin_numbers[i] < 0
                    pin_numbers[i] = abs(pin_numbers[i])
                    pinmap[pin_numbers[i]] = unit.children[i]
                if 'OC' in config and partrecord in config['OC']:
                    unit.oc_type =  config['OC'][partrecord]
                if 'ORIENT' in config and partrecord in config['ORIENT']:
                    orientdata = [int(num) for num in config['ORIENT'][partrecord].split(' ') if len(num.strip()) > 0]
                    unit.orientation = orientdata
                if 'PROG' in config and partrecord in config['PROG']:
                    unit.prog_data = config['PROG'][partrecord]
            except:
                print("Failed to create type", cmd)
    if 'WIRES' in config:
        for wirerecord in config['WIRES']:
            pins = config['WIRES'][wirerecord]
            pin_numbers = [int(pinnum) for pinnum in pins.split(' ') if pinnum.strip().isdigit()]
            for i in range(0, len(pin_numbers), 2):
                src = pin_numbers[i]
                dst = pin_numbers[i + 1]
                if src not in pinmap or dst not in pinmap: continue
                a= pinmap[src]
                b= pinmap[dst]
                a.route(b)

def read_file(filename):
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    config.read(filename)
    load_from_config(config)

def dup_selected(dx,dy):
    f = io.StringIO()
    config = write_file(f, selected=True)
    f.seek(0)
    load_from_config(config, dx=dx, dy=dy)

def dump():
    f = io.StringIO()
    config = write_file(f, )
    f.seek(0)
    print(f.read())
    load_from_config(config, dx=50, dy=50)


def saveas():
    filename = tkinter.filedialog.asksaveasfilename(
        defaultextension='.gate',
        filetypes=[('Logic simulator files', '*.gate'), ('All files', '*')])
    with open(filename, 'w') as f: write_file(f)


def load():
    filename = tkinter.filedialog.askopenfilename(filetypes=[('Logic simulator files', '*.gate'), ('All files', '*')])
    read_file(filename)
