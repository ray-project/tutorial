from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to use ray.wait to avoid waiting for
# slow tasks.

if __name__ == "__main__":
  ray.init(num_cpus=10, redirect_output=True)

  @ray.remote
  def f():
    x = np.random.uniform(0, 5)
    time.sleep(x)
    return x

  start_time = time.time()

  # This launches 10 tasks, each of which takes a random amount of time to
  # complete.
  #
  # EXERCISE: Use ray.wait to get the outputs of the first 5 tasks to finish.
  # Right now, we're waiting for all 10 tasks to finish.
  result_ids = [f.remote() for _ in range(20)]
  initial_results = ray.get(result_ids[:10])

  end_time = time.time()
  duration = end_time - start_time

  if duration > 2.75:
    print("FAILURE: The initial tasks were retrieved in {} seconds."
          .format(duration))
  else:
    print("SUCCESS: The initial tasks were retrieved in {} seconds."
          .format(duration))

  # EXERCISE: Wait for the remaining tasks to complete and double check that
  # they took longer than the first tasks that we got.
  remaining_results = ray.get(result_ids[10:])

  assert len(initial_results) == 10
  assert len(remaining_results) == 10

  for x in initial_results:
    for y in remaining_results:
      assert x < y
