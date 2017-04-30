def split_carry(a, n=4):
    ' return tuple n bits of a followed by boolean carry = True when next bit is set'
    return a & ((1 << n) - 1), bool(a >> n) & 1


alu_config = {  # function, name, number of input reigsters
    0: (lambda a, b, n=4: (a, False,), 'XFER', 1),
    1: (lambda a, b, n=4: (a ^ b, False), 'XOR', 2),
    2: (lambda a, b, n=4: (a & b, False,), 'AND', 2),
    3: (lambda a, b, n=4: (a | b, False), 'OR', 2),
    4: (lambda a, b, n=4: (~a, False), 'NOT', 1),
    5: (lambda a, b, n=4: split_carry(-a, n), 'NEG', 1),
    6: (lambda a, b, n=4: split_carry(a+1,n), 'INC', 1),
    7: (lambda a, b, n=4: split_carry(a-1,n), 'DEC', 1),
    0x8: (lambda a, b, n=4: split_carry(a + b,n), 'ADD', 2),
    0x9: (lambda a, b, n=4: split_carry(a + 1 + b,n), 'ADC', 2),
    0xA: (lambda a, b, n=4: split_carry(a - b,n), 'SUB', 2),
    0xB: (lambda a, b, n=4: split_carry(a - 1 - b,n), 'SBB', 2),
    0xC: (lambda a, b, n=4: split_carry(a << 1,n), 'SHL', 1),
    0xD: (lambda a, b, n=4: split_carry((a << 1) |  1,n), 'RLC', 1),
    0xE: (lambda a, b, n=4: split_carry(a >> 1,n), 'SHR', 1),
    0xF: (lambda a, b, n=4: split_carry((a >> 1) | 1 << n,n), 'RRC', 1),
}


def alu_fn(fn, a, b, n=4):
    return alu_config[fn][0](a, b, n)


def alu_info(fn):
    return alu_config[fn][1:3]
