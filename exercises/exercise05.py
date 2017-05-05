# The goal of this exercise is to show how to use ray.wait to avoid waiting for
# slow tasks.
#
# See the documentation for ray.wait at
# http://ray.readthedocs.io/en/latest/api.html#waiting-for-a-subset-of-tasks-to-finish.
#
# EXERCISE: This script starts 20 tasks, each of which takes a random amount of
# time to complete. We'd like to process the results in two batches (each of
# size 10). Change the code so that instead of waiting for a fixed set of 10
# tasks to finish, we make the first batch consist of the first 10 tasks that
# complete. The second batch should consist of the remaining tasks.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=20, redirect_output=True)

  @ray.remote
  def f(i):
    x = np.random.uniform(0, 5)
    time.sleep(x)
    return i, x

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(0.5)
  start_time = time.time()

  # This launches 20 tasks, each of which takes a random amount of time to
  # complete.
  result_ids = [f.remote(i) for i in range(20)]
  # Get one batch of tasks. Instead of waiting for a fixed subset of tasks, we
  # should instead use the first 10 tasks that finish.
  initial_results = ray.get(result_ids[:10])

  end_time = time.time()
  duration = end_time - start_time

  # Wait for the remaining tasks to complete.
  remaining_results = ray.get(result_ids[10:])

  assert len(initial_results) == 10
  assert len(remaining_results) == 10

  initial_indices = [result[0] for result in initial_results]
  initial_times = [result[1] for result in initial_results]
  remaining_indices = [result[0] for result in remaining_results]
  remaining_times = [result[1] for result in remaining_results]

  assert set(initial_indices + remaining_indices) == set(range(20))

  assert duration < 3, ("The initial batch of ten tasks was retrieved in "
                        "{} seconds. That's too slow.".format(duration))

  # Make sure the initial results actually completed first.
  assert max(initial_times) < min(remaining_times)

  print("Success! The example took {} seconds.".format(duration))
