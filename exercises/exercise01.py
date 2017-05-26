# The goal of this exercise is to show how to run simple tasks in parallel.
#
# EXERCISE: This script is too slow, and the computation is embarrassingly
# parallel. Use Ray to execute the functions in parallel to speed it up.
#
# NOTE: This exercise should work even if you have only one core on your
# machine because the function that we're parallelizing is just sleeping.
# However, in general you would not expect a larger speedup than the number of
# cores on the machine.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ray
import time


if __name__ == "__main__":
  # Start Ray. By default, Ray does not schedule more tasks concurrently than
  # there are CPUs. This example requires four tasks to run concurrently, so we
  # tell Ray that there are four CPUs. Usually this is not done and Ray
  # computes the number of CPUs using psutil.cpu_count(). The argument
  # redirect_output=True just hides some logging.
  ray.init(num_cpus=4, redirect_output=True)

  # This function is a proxy for a more interesting and computationally
  # intensive function.
  def slow_function(i):
    time.sleep(1)
    return i

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(2.0)
  start_time = time.time()

  # This loop is too slow. The calls to slow_function should happen in
  # parallel.
  results = []
  for i in range(4):
    results.append(slow_function(i))

  end_time = time.time()
  duration = end_time - start_time

  assert results == [0, 1, 2, 3]
  assert duration < 1.1, ("The loop took {} seconds. This is too slow."
                          .format(duration))
  assert duration >= 1, ("The loop took {} seconds. This is too fast."
                         .format(duration))

  print("Success! The example took {} seconds.".format(duration))
