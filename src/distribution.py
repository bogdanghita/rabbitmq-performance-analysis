import numpy as np
import math


class ExponentialSeries:

  def __init__(self):
    self.current = 1

  def next(self):
    res = self.current
    self.current *= 2
    return res


class AbstractRandom:

  def __init__(self, args):
    print args

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
  # d = PoissonRandom()
  # d = GeometricRandom()
  # d = ExponentialRandom()

  for i in range(105):
    print d.next()
