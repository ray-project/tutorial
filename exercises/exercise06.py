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

# The goal of this exercise is to show how to use send neural network weights
# between workers and the driver. Since, pickling and unpickling a TensorFlow
# graph can be inefficient or may not work at all, it is most efficient to ship
# the weights between processes as a dictionary of numpy arrays. We use the
# helper class ray.experimental.TensorFlowVariables to help with this. Similar
# techniques should work other neural net libraries.


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  # This actor contains a simple neural network.
  #
  # Exercise: Implement the set_weights and get_weights methods so that the
  # driver can retrieve the weights from the actor and set new weights on the
  # actor.
  @ray.actor
  class SimpleModel(object):
    def __init__(self):
      x_data = tf.placeholder(tf.float32, shape=[100])
      y_data = tf.placeholder(tf.float32, shape=[100])

      w = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
      b = tf.Variable(tf.zeros([1]))
      y = w * x_data + b

      self.loss = tf.reduce_mean(tf.square(y - y_data))
      optimizer = tf.train.GradientDescentOptimizer(0.5)
      grads = optimizer.compute_gradients(loss)
      self.train = optimizer.apply_gradients(grads)

      init = tf.global_variables_initializer()
      self.sess = tf.Session()

      self.sess.run(init)

    def set_weights(self, weights):
      # Exercise: Implement this.
      pass

    def get_weights(self):
      # Exercise: Implement this.
      pass

  # Create a few actors with the model.
  actors = [SimpleModel() for _ in range(4)]

  # EXERCISE: Get the weights from the actors.
  # FILL THIS IN.

  # EXERCISE: Average the weights.
  # FILL THIS IN.

  # EXERCISE: Set the average weights on the actors.
  # FILL THIS IN.
