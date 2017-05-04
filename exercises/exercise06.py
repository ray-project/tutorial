# The goal of this exercise is to show how to use ray.wait to process tasks in
# the order that they finish.
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
  ray.init(num_cpus=5, redirect_output=True)

  @ray.remote
  def f():
    time.sleep(np.random.uniform(0, 10))
    return time.time()

  start_time = time.time()

  result_ids = [f.remote() for _ in range(10)]

  # Get the results.
  results = []
  for result_id in result_ids:
    result = ray.get(result_id)
    results.append(result)
    print("Processing result which finished after {} seconds."
          .format(result - start_time))

  assert results == sorted(results), ("The results were not processed in the "
                                      "order that they finished.")
