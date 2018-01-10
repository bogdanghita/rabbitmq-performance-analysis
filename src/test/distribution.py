import numpy as np

n = 10

a = np.random.normal(loc=0.0, scale=1.0, size=n)
print a

a = np.random.poisson(lam=1.0, size=n)
print a

a = np.random.geometric(p=0.35, size=n)
print a

a = np.random.exponential(scale=1.0, size=n)
print a