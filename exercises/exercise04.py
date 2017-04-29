from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to pass object IDs into remote
# functions to encode dependencies between tasks.

if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  @ray.remote
  def create_data():
    return np.ones(10000)

  # This is a proxy for an expensive aggregation step (which is also
  # commutative and associative so it should be used in a tree-reduce).
  def aggregate_data(x, y):
    time.sleep(0.5)
    return x + y

  vector_ids = [create_data.remote() for _ in range(8)]

  start_time = time.time()

  # Here we aggregate all of the data by getting it on the driver and then
  # repeatedly calling aggregate_data. However, this could be done faster by
  # making aggregate_data a remote function and aggregating the data in a
  # tree-like fashion.
  vectors = ray.get(vector_ids)
  result = vectors[0]
  for vector in vectors[1:]:
    result = aggregate_data(result, vector)

  end_time = time.time()
  duration = end_time - start_time

  if duration < 3.5 / 2:
    print("SUCCESS: The results were aggregated in {} seconds."
          .format(duration))
  else:
    print("FAILURE: The results were aggregated in {} seconds."
          .format(duration))
