# The goal of this exercise is to illustrate how to use actors to avoid
# expensive initializations.
#
# EXERCISE: Avoid the overhead of constantly recreating the "Foo" object inside
# of the remote function by using actors.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  class Foo(object):
    def __init__(self):
      # This class takes a long time to initialize. For example, maybe it
      # constructs a neural net and places the neural net on a GPU.
      time.sleep(1)

    def do_something(self):
      # However, the class can be used very quickly.
      time.sleep(0.1)
      return 1

  # Here, we define a remote function that creates a Foo object and uses it to
  # do something simple. There's no good reason to repeatedly recreate the Foo
  # object.
  @ray.remote
  def do_something():
    f = Foo()
    return f.do_something()

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(0.5)
  start_time = time.time()

  results = ray.get([do_something.remote() for _ in range(16)])

  end_time = time.time()
  duration = end_time - start_time

  assert results == 16 * [1]
  assert duration < 2, ("The experiments ran in {} seconds. This is too "
                        "slow.".format(duration))

  print("Success! The example took {} seconds.".format(duration))
