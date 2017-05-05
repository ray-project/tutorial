# The goal of this exercise is to combine a handful of lessons in a single
# example and to get some practice parallelizing serial code. In this exercise,
# we create a neural network and a gym environment and use the network to do
# some rollouts (that is, we use the neural net to choose actions to take in
# the environment). However, all of the rollouts are done serially.
#
# EXERCISE: Change this code to do rollouts in parallel. To avoid recreating
# the neural net over and over, you may want to use actors.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import psutil
import ray
import tensorflow as tf
import time

from ray_tutorial.reinforce.env import BatchedEnv
from ray_tutorial.reinforce.policy import ProximalPolicyLoss
from ray_tutorial.reinforce.filter import MeanStdFilter
from ray_tutorial.reinforce.rollout import rollouts, add_advantage_values

from ray_tutorial.reinforce.env import (NoPreprocessor, AtariRamPreprocessor,
                                        AtariPixelPreprocessor)
from ray_tutorial.reinforce.models.fc_net import fc_net
from ray_tutorial.reinforce.models.vision_net import vision_net

config = {"kl_coeff": 0.2,
          "num_sgd_iter": 30,
          "sgd_stepsize": 5e-5,
          "sgd_batchsize": 128,
          "entropy_coeff": 0.0,
          "clip_param": 0.3,
          "kl_target": 0.01,
          "timesteps_per_batch": 40000}


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  # For a more interesting example, try this with the following values. Note
  # that this will require installing gym with the atari environments. You'll
  # probably want to use a smaller batchsize for this.
  #
  #     name = "Pong-v0"
  #     preprocessor = AtariPixelPreprocessor()

  name = "CartPole-v0"
  batchsize = 100
  preprocessor = NoPreprocessor()
  gamma = 0.995
  lam = 1.0
  horizon = 2000

  class Environment(object):
    def __init__(self):
      # Create a simulator environment. This is a wrapper containing a batch of gym
      # environments. The simulator can be simulated with "env.step(action)", which
      # is called within the "rollouts" function below.
      self.env = BatchedEnv(name, batchsize, preprocessor=preprocessor)

      # Create a neural net policy. Note that we create the neural net inside its
      # own graph. This can help avoid variable name collisions. It shouldn't
      # matter in this example, but if you create a neural net inside of a remote
      # function, and multiple tasks execute that remote function on the same
      # worker, then this can lead to variable name collisions.
      with tf.Graph().as_default():
        sess = tf.Session()
        if preprocessor.shape is None:
          preprocessor.shape = self.env.observation_space.shape
        self.policy = ProximalPolicyLoss(self.env.observation_space,
            self.env.action_space, preprocessor, config, sess)
        self.observation_filter = MeanStdFilter(preprocessor.shape, clip=None)
        self.reward_filter = MeanStdFilter((), clip=None)
        sess.run(tf.global_variables_initializer())

  @ray.remote
  def rollout():
    environment = Environment()

    # Collect some rollouts.
    trajectories = []
    for _ in range(5):
      trajectory = rollouts(environment.policy, environment.env, horizon,
                            environment.observation_filter,
                            environment.reward_filter)
      add_advantage_values(trajectory, gamma, lam, environment.reward_filter)
      trajectories.append(trajectory)
    return trajectories

  # Sleep a little to improve the accuracy of the timing measurements below.
  time.sleep(2.0)
  start_time = time.time()

  # Do some rollouts serially. These should be done in parallel.
  rollouts = [rollout.remote() for _ in range(4)]
  rollouts = ray.get(rollouts)
  rollouts = [trajectory for rollout in rollouts for trajectory in rollout]

  end_time = time.time()
  duration = end_time - start_time

  expected_duration = np.ceil(20 / psutil.cpu_count()) * 0.5
  assert duration < expected_duration, ("Rollouts took {} seconds."
                                        .format(duration))

  print("Success! The example took {} seconds.".format(duration))
