from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to create an actor and to call actor
# methods.
#
# Sometimes you need a "worker" process to have "state". For example, that
# state might be a neural network, a simulator environment, a counter, or
# something else entirely. However, remote functions are side-effect free. That
# is, they operate on inputs and produce outputs, but don't change the state of
# the worker they execute on.
#
# Actors are different. When we instantiate an actor, a brand new worker is
# created, and all methods that are called on that actor are executed on the
# newly created worker.
#
# This means that with a single actor, no parallelism can be achieved because
# calls to the actor's methods will be executed one at a time. However,
# multiple actors can be created and methods can be executed on them in
# parallel.
#
# EXERCISE:

if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  # Here, we define a remote function that creates a Foo object and uses it to
  # do something simple. In this case, there's no good reason to repeatedly
  # recreate the Foo object.
  #
  # EXERCISE: Speed up this example by making the Foo class an actor.

  class Foo(object):
    def __init__(self):
      # This class takes a long time to initialize.
      time.sleep(1)

    def do_something(self):
      # However, using the class can be quick.
      return 1

  @ray.remote
  def do_something():
    f = Foo()
    return f.do_something()

  start_time = time.time()

  ray.get([do_something.remote() for _ in range(16)])

  end_time = time.time()
  duration = end_time - start_time

  assert duration < 2, ("The experiments ran in {} seconds. This is too "
                        "slow.".format(duration))
