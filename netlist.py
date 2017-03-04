class DumpTrace:
    def __init__(self, f, *args, **kw):
        self.f = f

    def __call__(self, *args, **kw):
        print("%s (" % self.f.name, args, kw, ')')
        self.f(*args, **kw)


groups = []


def connect(a, b):
    global groups
    connection = (min(a, b), max(a, b))
    selected = {connection}
    for group in groups[:]:  # [:] use a copy of groups so group can be deleted within loop
        for pair in group:
            for value in pair:
                if value in connection:
                    # merge groups together that contain pins that are bein connected into the selected group
                    selected = selected.union(group)
                    if group in groups: groups.remove(group)
    groups.append(selected)


def group_of(a, b=None):
    if b is None:
        result = [group for group in groups[:] if any(a in pair for pair in group)]
        return result[0] if result else None
    else:
        return [group for group in groups[:] if sorted(a, b) in group][0]


def direct_connections_to(a):
    g = group_of(a)
    return [x for x in g if a in x]


def disconnect(a, b=None):
    connection = (min(a, b), max(a, b))
    for group in groups:
        if connection in group:
            groups.remove(group)
            group.remove(connection)
            for i in group: connect(*i)
            break
