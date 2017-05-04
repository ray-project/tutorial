# Like the previous exercise, the goal of this exercise is to show how to pass
# object IDs into remote functions to encode dependencies between tasks. The
# code in this example generates a handful of arrays and then aggregates them
# in a tree-like pattern.
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
  ray.init(num_cpus=8, redirect_output=True)

  # This is a proxy for a function which generates some data.
  def create_data(i):
    time.sleep(0.1)
    return i * np.ones(10000)

  # This is a proxy for an expensive aggregation step (which is also
  # commutative and associative so it can be used in a tree-reduce).
  def aggregate_data(x, y):
    time.sleep(0.5)
    return x * y

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(0.5)
  start_time = time.time()

  # Here we generate some data. This could be done in parallel.
  vectors = [create_data(i + 1) for i in range(8)]

  # Here we aggregate all of the data by getting it on the driver and then
  # repeatedly calling aggregate_data. However, this could be done faster by
  # making aggregate_data a remote function and aggregating the data in a
  # tree-like fashion.
  #
  # NOTE: A direct translation of the code below to use Ray will not result in
  # a speedup because the underlying graph of dependencies between the tasks is
  # essentially linear. There are a handful of ways to do this, and the
  # aggregation can actually be done cleverly in two lines.
  result = vectors[0]
  for vector in vectors[1:]:
    result = aggregate_data(result, vector)

  end_time = time.time()
  duration = end_time - start_time

  assert np.all(result == (8 * 7 * 6 * 5 * 4 * 3 * 2) * np.ones(10000))
  assert duration < 0.1 + 1.5 + 0.3, ("FAILURE: The data generation and "
                                      "aggregation took {} seconds. This is "
                                      "too slow".format(duration))
