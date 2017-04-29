from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gym
import ray
import time

# The goal of this exercise is to show how to run simple tasks in parallel.

if __name__ == "__main__":
  # Start Ray. By default, Ray does not schedule more tasks concurrently than
  # there are CPUs. This example requires four tasks to run concurrently, so we
  # tell Ray that there are four CPUs. Usually this is not done and Ray
  # computes the number of CPUs using psutil.cpu_count().
  ray.init(num_cpus=4, redirect_output=True)

  # This function is a proxy for a more interesting and computationally
  # intensive function.
  def slow_function():
    time.sleep(1)

  start_time = time.time()

  # This loop is too slow. The calls to slow_function should happen in
  # parallel.
  for _ in range(4):
    slow_function()

  end_time = time.time()
  duration = end_time - start_time

  assert duration < 1.1, ("The loop took {} seconds. This is too slow."
                          .format(duration))
