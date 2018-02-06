#!/usr/bin/env python3

import numpy as np
import math
import sys


class ExponentialSeries:

  def __init__(self):
    self.current = 1

  def next(self):
    res = self.current
    self.current *= 2
    return res


class ProgressiveSeries:

  def __init__(self, start=0, increment=10):
    self.current = start
    self.inc = increment

  def next(self):
    res = self.current
    self.current += self.inc
    return res


class AbstractRandom:

  def __init__(self, args):
    self.size = 100
    self.args = args

    self.buffer = self.distribution(args)
    self.idx = 0

  def distribution(self, args):
    raise NotImplementedError()

  def next(self):
    res = self.buffer[self.idx]
    self.idx += 1
    if self.idx == self.size:
      self.buffer = self.distribution(self.args)
      self.idx = 0
    return res


class GaussianRandom(AbstractRandom):

  def __init__(self, loc=0.0, scale=1.0):
    AbstractRandom.__init__(self, dict(loc=loc, scale=scale))

  def distribution(self, args):
    return np.random.normal(args['loc'], args['scale'], self.size)


class PoissonRandom(AbstractRandom):

  def __init__(self, lam=1.0):
    AbstractRandom.__init__(self, dict(lam=lam))

  def distribution(self, args):
    return np.random.poisson(args['lam'], self.size)


class GeometricRandom(AbstractRandom):

  def __init__(self, p=0.5):
    AbstractRandom.__init__(self, dict(p=p))

  def distribution(self, args):
    return np.random.geometric(args['p'], self.size)


class ExponentialRandom(AbstractRandom):

  def __init__(self, scale=1.0):
    AbstractRandom.__init__(self, dict(scale=scale))

  def distribution(self, args):
    return np.random.exponential(args['scale'], self.size)



if __name__ == "__main__":
  
  d = GaussianRandom()
  # (-5.60052780212,5.23051130879)

  # d = PoissonRandom()
  # (0,10)

  # d = GeometricRandom()
  # (1,25)

  # d = ExponentialRandom()
  # (8.62551424182e-08,15.6896301305)

  min_v = sys.maxint
  max_v = -sys.maxint - 1
  for i in range(100):
    v = d.next()
    if v < min_v:
      min_v = v
    if v > max_v:
      max_v = v
    print(v)
  print("({},{})".format(min_v, max_v))
