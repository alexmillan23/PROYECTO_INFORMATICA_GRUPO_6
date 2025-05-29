from node import *

class Segment:
    def __init__(self, name, orig, dest):
        self.name = name
        self.orig = orig
        self.dest = dest
        self.cost = Distance(orig, dest)

def CalcCost(segment):
    return Distance(segment.orig, segment.dest)