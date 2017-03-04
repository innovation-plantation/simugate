import functools

# ieee1164 logic
#  Strong Weak                     #  Other
#      0   L     False signal      #     Z   No signal
#      1   H     True signal       #     U   Uninitialized signal
#      X   W     Unknown signal    #     -   Irrelevant signal
#
oc = '\u235a'  # IEEE 91 open collector output symbol: underlined diamond
zs = '\u9661'  # IEEE 91 3-state output symbol: triangle pointing down
thick, thin = 5, 3
logic = 'UX01ZWLH-'
color = {'U': '#00ffff', 'X': '#ffa000', '0': '#404040', '1': '#c00000',
         'Z': '#8880ff', 'W': '#ffa000', 'L': '#404040', 'H': '#c00000', '-': 'green'}
width = {'U': thick, 'X': thick, '0': thick, '1': thick,
         'Z': thin, 'W': thin, 'L': thin, 'H': thin, '-': thin}
index = {'U': 0, 'X': 1, '0': 2, '1': 3, 'Z': 4, 'W': 5, 'L': 6, 'H': 7, '-': 8}
buswidth = 10
buscolor = 'lightblue'


def ttfn(tt, x): return functools.reduce(lambda a, b: tt[index[a]][index[b]], x)


wirett = (
    # UX01ZWLH-
    'UUUUUUUUU',  # U
    'UXXXXXXXX',  # X
    'UX0X0000X',  # 0
    'UXX11111X',  # 1
    'UX01ZWLHX',  # Z
    'UX01WWWWX',  # W
    'UX01LWLWX',  # L
    'UX01HWWHX',  # H
    'UXXXXXXXX')  # -


def wirefn(*x): return ttfn(wirett, x)


npntt = (  # active high B: L or Z output
    # UX01ZWLH-:B  # E:
    r'UUZUZUZUU',  # U
    r'UXZXZXZXX',  # X
    r'UXZ0ZXZ0X',  # 0
    r'UXZZZXZZX',  # 1
    r'UXZZZXZZX',  # Z
    r'UXZWZXZWX',  # W
    r'UXZLZXZLX',  # L
    r'UXZZZXZZX',  # H
    r'UXZXZXZXX')  # -


def npnfn(*x): return ttfn(npntt, x)


pnptt = (  # active low B: H or Z output
    # UX01ZWLH-:B  # E:
    r'UUUZZUUZU',  # U
    r'UXXZZXXZX',  # X
    r'UXZZZXZZX',  # 0
    r'UX1ZZX1ZX',  # 1
    r'UXZZZXZZX',  # Z
    r'UXWZZXWZX',  # W
    r'UXZZZXZZX',  # L
    r'UXHZZXHZX',  # H
    r'UXXZZXXZX')  # -


def pnpfn(*x): return ttfn(pnptt, x)


andtt = (
    # UX01ZWLH-
    'UU0UUU0UU',  # U
    'UX0XXX0XX',  # X
    '000000000',  # 0
    'UX01XX01X',  # 1
    'UX0XXX0XX',  # Z
    'UX0XXX0XX',  # W
    '000000000',  # L
    'UX01XX01X',  # H
    'UX0XXX0XX')  # -


def andfn(*x): return ttfn(andtt, x)


nandtt = (
    # UX01ZWLH-
    'UU1UUU1UU',  # U
    'UX1XXX1XX',  # X
    '111111111',  # 0
    'UX10XX10X',  # 1
    'UX1XXX1XX',  # Z
    'UX1XXX1XX',  # W
    '111111111',  # L
    'UX10XX10X',  # H
    'UX1XXX1XX')  # -


def nandfn(*x): return ttfn(nandtt, x)


ocnandtt = (
    # UX01ZWLH-
    'UUZUUUZUU',  # U
    'UXZXXXZXX',  # X
    'ZZZZZZZZZ',  # 0
    'UXZ0XXZ0X',  # 1
    'UXZXXXZXX',  # Z
    'UXZXXXZXX',  # W
    'ZZZZZZZZZ',  # L
    'UXZ0XXZ0X',  # H
    'UXZXXXZXX')  # -


def ocnandfn(*x): return ttfn(ocnandtt, x)


ortt = (
    # UX01ZWLH-
    'UUU1UUU1U',  # U
    'UXX1XXX1X',  # X
    'UX01XX01X',  # 0
    '111111111',  # 1
    'UXX1XXX1X',  # Z
    'UXX1XXX1X',  # W
    'UX01XX01X',  # L
    '111111111',  # H
    'UXX1XXX1X')  # -


def orfn(*x): return ttfn(ortt, x)


nortt = (
    # UX01ZWLH-
    'UUU0UUU1U',  # U
    'UXX0XXX0X',  # X
    'UX10XX10X',  # 0
    '000000000',  # 1
    'UXX0XXX0X',  # Z
    'UXX0XXX0X',  # W
    'UX10XX10X',  # L
    '000000000',  # H
    'UXX0XXX0X')  # -


def norfn(*x): return ttfn(nortt, x)


ocnortt = (
    # UX01ZWLH-
    'UUU0UUUZU',  # U
    'UXX0XXX0X',  # X
    'UXZ0XXZ0X',  # 0
    '000000000',  # 1
    'UXX0XXX0X',  # Z
    'UXX0XXX0X',  # W
    'UXZ0XXZ0X',  # L
    '000000000',  # H
    'UXX0XXX0X')  # -


def ocnorfn(*x): return ttfn(ocnortt, x)


xortt = (
    # UX01ZWLH-
    'UUUUUUUUU',  # U
    'UXXXXXXXX',  # X
    'UX01XX01X',  # 0
    'UX10XX10X',  # 1
    'UXXXXXXXX',  # Z
    'UXXXXXXXX',  # W
    'UX01XX01X',  # L
    'UX10XX10X',  # H
    'UXXXXXXXX')  # -


def xorfn(*x): return ttfn(xortt, x)


#        UX01ZWLH-
nottt = 'UX10XX10X';


def notfn(*x): return nottt[index[wirefn(*x)]]


#        UX01ZWLH-
buftt = 'UX01XX01X';


def buffn(*x): return buftt[index[wirefn(*x)]]


diantt = (  # diode annode output for annode and cathode inputs A--|>|--C
    # UX01ZWLH-:A  # C:
    'UUU0UUUUU',  # U
    'UXXZZZZZZ',  # X
    'UZZZZZZZZ',  # 0
    '0XXZZZZZZ',  # 1
    'UX0ZZWLZZ',  # Z
    'UX0ZZWWZZ',  # W
    'UX0ZZZZZZ',  # L
    '0X0ZZWWZZ',  # H
    'UZZZZZZZZ')  # -


def dianfn(*x): return ttfn(diantt, x)


dicatt = (  # diode cathode output for annode and cathode inputs A--|>|--C
    # UX01ZWLH-:A  # C:
    'UUU0UUUUU',  # U
    'UXXZXXXXZ',  # X
    'UZZZZZZZZ',  # 0
    '0XXZ1111Z',  # 1
    'UZZZZZZZZ',  # Z
    'UZZZWWWWZ',  # W
    'UZZZZZZZZ',  # L
    '0ZZZHWWZZ',  # H
    'UZZZZZZZZ')  # -


def dicafn(*x): return ttfn(dicatt, x)
