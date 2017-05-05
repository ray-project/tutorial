# The goal of this exercise is to illustrate how to speed up serialization by
# using ray.put.
#
# When objects are passed into a remote function, we put them in the object
# store under the hood. That is, if "f" is a remote function, the code
#
#    x = np.zeros(1000)
#    f.remote(x)
#
# is essentially transformed under the hood to
#
#    x = np.zeros(1000)
#    x_id = ray.put(x)
#    f.remote(x_id)
#
# The call to ray.put copies the numpy array into the shared-memory object
# store, from where it can be read by all of the worker processes (without
# additional copying). However, if you do something like
#
#     for i in range(10):
#       f.remote(x)
#
# then 10 copies of the array will be placed into the object store. This takes
# up more memory in the object store than is necessary, and it also takes time
# to copy the array into the object store over and over. This can be made more
# efficient by placing the array in the object store only once as follows.
#
#     x_id = ray.put(x)
#     for i in range(10):
#       f.remote(x_id)
#
# EXERCISE: Speed up the code below and reduce the memory footprint by calling
# ray.put on the neural net weights before passing them into the remote
# functions.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=20, redirect_output=True)

  neural_net_weights = {"variable{}".format(i): np.random.normal(size=1000000)
                        for i in range(50)}

  # For fun, you may be interested in comparing the following times, for
  # different values of "neural_net_weights". This is best done in an ipython
  # interpreter.
  #
  #     %time x_id = ray.put(neural_net_weights)
  #     %time x_val = ray.get(x_id)
  #
  #     import pickle
  #     %time serialized = pickle.dumps(neural_net_weights)
  #     %time deserialized = pickle.loads(serialized)
  #
  # Note that when you call ray.put, in addition to serializing the object, we
  # are copying it into shared memory where it can be efficiently accessed by
  # other workers on the same machine.

  @ray.remote
  def use_weights(weights, i):
    return i

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(2.0)
  start_time = time.time()

  neural_net_weights = ray.put(neural_net_weights)
  results = ray.get([use_weights.remote(neural_net_weights, i)
                     for i in range(20)])

  end_time = time.time()
  duration = end_time - start_time

  assert results == list(range(20))
  assert duration < 1, ("The experiments ran in {} seconds. This is too "
                        "slow.".format(duration))

  print("Success! The example took {} seconds.".format(duration))
