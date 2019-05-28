# The goal of this exercise is to show how to use ray.wait to process tasks in
# the order that they finish.
#
# See the documentation for ray.wait at
# http://ray.readthedocs.io/en/latest/api.html#waiting-for-a-subset-of-tasks-to-finish.
#
# The code below runs 10 tasks and retrieves the results in the order that the
# tasks were launched. However, since each task takes a random amount of time
# to finish, we could instead process the tasks in the order that they finish.
#
# EXERCISE: Change the code below to use ray.wait to get the results of the
# tasks in the order that they complete.
#
# Note that it would be a simple modification to maintain a pool of 10
# experiments and to start a new experiment whenever one finishes.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=5)

  @ray.remote
  def f():
    time.sleep(np.random.uniform(0, 10))
    return time.time()

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(2.0)
  start_time = time.time()

  result_ids = [f.remote() for _ in range(10)]

  # Get the results.
  results = []
  while len(result_ids) > 0:
    result, result_ids = ray.wait(result_ids)
    result = ray.get(result[0])
    results.append(result)
    print("Processing result which finished after {} seconds."
          .format(result - start_time))

  duration = time.time() - start_time

  assert results == sorted(results), ("The results were not processed in the "
                                      "order that they finished.")

  print("Success! The example took {} seconds.".format(duration))
