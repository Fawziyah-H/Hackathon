# normalise tool
# By Robert Shaw

def normalise(x, max):
    if abs(x) > max:
        return 1*(abs(x)/x)
    else:
        return x / max
