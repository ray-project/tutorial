from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to create an actor and to call actor
# methods.

if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  class Foo(object):
    def __init__(self):
      self.counter = 0

    def increment(self):
      time.sleep(0.5)
      self.counter += 1
      return self.counter

  # Create two Foo objects.
  f1 = Foo()
  f2 = Foo()

  start_time = time.time()

  # We want to parallelize this code. However, it is not straightforward to
  # make "increment" a remote function, because state is shared (the value of
  # "self.counter") between subsequent calls to "increment". In this case, it
  # makes sense to use actors.
  results = []
  for _ in range(5):
    results.append(f1.increment())
    results.append(f2.increment())

  end_time = time.time()
  duration = end_time - start_time

  assert results == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

  assert duration < 3, ("The experiments ran in {} seconds. This is too "
                        "slow.".format(duration))
