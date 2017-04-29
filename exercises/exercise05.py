from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time

# The goal of this exercise is to show how to create nested tasks by calling a
# remote function inside of another remote function.

if __name__ == "__main__":
  ray.init(num_cpus=12, redirect_output=True)

  # This is a function that represents some sort of experiment. It repeatedly
  # calls the helper function, and some of the calls could be done in parallel.
  #
  # EXERCISE: Make helper a remote function so that the calls to helper can be
  # done in parallel.
  #
  # LIMITATION: The definition of "helper" must come before the definition of
  # "experiment" because as soon as experiment is defined, it will be pickled
  # and shipped to the workers, and so if helper hasn't been defined yet, the
  # definition will be incomplete.

  def helper():
    time.sleep(0.1)
    return 1

  @ray.remote
  def experiment():
    results = []
    for i in range(10):
      results.append(sum([helper() for _ in range(5)]))
    return results

  start_time = time.time()

  # Run two experiments in parallel.
  experiment_id1 = experiment.remote()
  experiment_id2 = experiment.remote()

  ray.get([experiment_id1, experiment_id2])

  end_time = time.time()
  duration = end_time - start_time

  if duration < 1.5:
    print("SUCCESS: The experiments ran in {} seconds.".format(duration))
  else:
    print("FAILURE: The experiments ran in {} seconds.".format(duration))
