from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to use ray.wait to process tasks in
# the order that they finish.

if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

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

  if results == sorted(results):
    print("SUCCESS: The results were processed in the order they finished.")
  else:
    print("FAILURE: The results were not processed in the order they "
          "finished.")
