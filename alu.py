def split_carry(a, n=4):
    ' return tuple n bits of a followed by boolean carry = True when next bit is set'
    return a & ((1 << n) - 1), bool(a >> n) & 1


alu_config = {
    0: (lambda a, b, n=4: (a, None,), 'XFER', 1),
    1: (lambda a, b, n=4: (a ^ b, None), 'XOR', 2),
    2: (lambda a, b, n=4: (a & b, None,), 'AND', 2),
    3: (lambda a, b, n=4: (a | b, None), 'OR', 2),
    4: (lambda a, b, n=4: (~a, None), 'NOT', 1),
    5: (lambda a, b, n=4: split_carry(-a, n), 'NEG', 1),
    6: (lambda a, b, n=4: split_carry(0, n), 'CLR', 0),
    7: (lambda a, b, n=4: split_carry(-1), 'SET', 0),
    0x8: (lambda a, b, n=4: split_carry(a + b), 'ADD', 2),
    0x9: (lambda a, b, n=4: split_carry(a + 1 + b), 'ADC', 2),
    0xA: (lambda a, b, c, n=4: split_carry(a - b), 'SUB', 2),
    0xB: (lambda a, b, n=4: split_carry(a - 1 - b), 'SBB', 2),
    0xC: (lambda a, b, n=4: split_carry(a << 1), 'RAL', 2),
    0xD: (lambda a, b, c, n=4: split_carry(a << 1 | 1), 'RLC', 1),
    0xE: (lambda a, b, n=4: split_carry(a >> 1), 'ROR', 2),
    0xF: (lambda a, b, c, n=4: split_carry(a >> 1 | 1), 'RRC', 1),
}


def alu_fn(fn, a, b, n=4):
    return alu_config[fn][0](a, b, n)


def alu_info(fn):
    return alu_config[fn][1:3]
