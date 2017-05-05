# The goal of this exercise is to show how to pass object IDs into remote
# functions to encode dependencies between tasks. In this case, we construct a
# sequence of tasks, each of which depends on the previous. Within each
# sequence, tasks are executed serially, but multiple sequences can be executed
# in parallel.
#
# EXERCISE: This script is too slow, use Ray to parallelize the computation
# below.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  # This function is a proxy for a more interesting and computationally
  # intensive function.
  def slow_function(i):
    time.sleep(np.random.uniform(0, 0.1))
    return i + 1

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(2.0)
  start_time = time.time()

  # This loop is too slow. Some of the calls to slow_function should happen in
  # parallel. Note that some of the calls may use the outputs of other calls.
  # The underlying computation graph encoding the dependencies between these
  # tasks consists of four chains of length twenty.
  results = []
  for i in range(4):
    x = 100 * i
    for j in range(20):
      x = slow_function(x)
    results.append(x)

  end_time = time.time()
  duration = end_time - start_time

  assert results == [20, 120, 220, 320]
  assert duration < 1.3, ("The loop took {} seconds. This is too slow."
                          .format(duration))

  print("Success! The example took {} seconds.".format(duration))
