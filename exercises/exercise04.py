# The goal of this exercise is to show how to create nested tasks by calling a
# remote function inside of another remote function. There is an outer function
# which is called multiple times, and the outer function calls an inner
# function multiple times. Both the outer and inner calls can be done in
# parallel.
#
# EXERCISE: Use Ray to speed up this example by parallelizing both the calls to
# "experiment" and the calls to "helper".

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=12, redirect_output=True)

  # LIMITATION: The definition of "helper" must come before the definition of
  # "experiment" because as soon as experiment is defined (assuming you make
  # experiment a remote function), it will be pickled and shipped to the
  # workers, and so if helper hasn't been defined yet, the definition will be
  # incomplete.
  def helper():
    time.sleep(0.03)
    return 1

  # This is a function that represents some sort of experiment. It repeatedly
  # calls the helper function, and some of the calls could be done in parallel.
  def experiment():
    results = []
    for i in range(10):
      results.append(sum([helper() for _ in range(5)]))
    return results

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(0.5)
  start_time = time.time()

  # Run two experiments. These could be done in parallel.
  experiment1 = experiment()
  experiment2 = experiment()

  end_time = time.time()
  duration = end_time - start_time

  assert sum(experiment1) == 50
  assert sum(experiment2) == 50
  assert duration < 0.35, ("The experiments ran in {} seconds. This is too "
                          "slow.".format(duration))

  print("Success! The example took {} seconds.".format(duration))
