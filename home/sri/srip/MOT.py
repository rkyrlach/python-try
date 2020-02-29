#!/usr/bin/python

class MOT:

#  def __init__(self, P, I, D, min, max, dz, tier):
  def init(self, P, I, D, min, max, dz, tier):
    print(P,I,D,min,max,dz,tier)

  def motInit (self):
    P = 50.0
    I = 10.4
    D = 20.2
    min = 8
    max = 17
    dz = 8
    tier = 4
    vals = [P, I, D, min, max, dz, tier]
    return vals

