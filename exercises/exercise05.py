from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
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

# The goal of this exercise is to show how to use actors. In this exercise, we
# define a remote function which creates a neural network and a gym
# environment and uses the network to do a rollout in the environment. However,
# every time a rollout is done, a new network is created. If the network
# creation is expensive (e.g., the network is placed on a GPU), then this will
# be slow.

config = {"kl_coeff": 0.2,
          "num_sgd_iter": 30,
          "sgd_stepsize": 5e-5,
          "sgd_batchsize": 128,
          "entropy_coeff": 0.0,
          "clip_param": 0.3,
          "kl_target": 0.01,
          "timesteps_per_batch": 40000}


if __name__ == "__main__":
  # Tell Ray to serialize objects of these types using pickle.
  ray.register_class(NoPreprocessor, pickle=True)
  ray.register_class(AtariRamPreprocessor, pickle=True)
  ray.register_class(AtariPixelPreprocessor, pickle=True)

  ray.init(num_cpus=4, redirect_output=True)

  # This remote function creates a neural net and a gym environment and does a
  # rollout. A new network is created every time this remote function is
  # called.
  #
  # Exercise: Change this remote function to be a method of an actor so that
  # the neural net and the gym environment are only created once in the actor's
  # constructor.
  @ray.remote
  def rollout(name, batchsize, preprocessor, config, gamma, lam, horizon):
    # Initialize the network and the environment.
    env = BatchedEnv(name, batchsize, preprocessor=preprocessor)
    if preprocessor.shape is None:
      preprocessor.shape = env.observation_space.shape
    # Note that we create the neural net inside its own graph. This can be
    # important because we will call this rollout function multiple times, and
    # some of the tasks will be scheduled on the same workers. This will result
    # in the graph being created multiple times on the same worker, and there
    # can be collisions in the variable names.
    with tf.Graph().as_default():
      sess = tf.Session()
      policy = ProximalPolicyLoss(env.observation_space, env.action_space, preprocessor, config, sess)
      # optimizer = tf.train.AdamOptimizer(config["sgd_stepsize"])
      # train_op = optimizer.minimize(policy.loss)
      # variables = ray.experimental.TensorFlowVariables(policy.loss, sess)
      observation_filter = MeanStdFilter(preprocessor.shape, clip=None)
      reward_filter = MeanStdFilter((), clip=5.0)
      sess.run(tf.global_variables_initializer())

    # Collect some rollouts.
    trajectory = rollouts(policy, env, horizon, observation_filter, reward_filter)
    add_advantage_values(trajectory, gamma, lam, reward_filter)

    return trajectory

  # Run two experiments in parallel.
  rollout_ids = [rollout.remote("Pong-v0", 1, AtariPixelPreprocessor(), config, 0.995, 1.0, 2000)
                 for _ in range(8)]
  rollouts = ray.get(rollout_ids)
