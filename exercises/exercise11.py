# The goal of this exercise is to show how to send neural network weights
# between workers and the driver.
#
# Since pickling and unpickling a TensorFlow graph can be inefficient or may
# not work at all, it is most efficient to ship the weights between processes
# as a dictionary of numpy arrays.
#
# We provide the helper class ray.experimental.TensorFlowVariables to help with
# get and set weights. Similar techniques should work other neural net
# libraries.
#
# Consider the following neural net definition.
#
#     import tensorflow as tf
#
#     x_data = tf.placeholder(tf.float32, shape=[100])
#     y_data = tf.placeholder(tf.float32, shape=[100])
#
#     w = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
#     b = tf.Variable(tf.zeros([1]))
#     y = w * x_data + b
#
#     loss = tf.reduce_mean(tf.square(y - y_data))
#     optimizer = tf.train.GradientDescentOptimizer(0.5)
#     grads = optimizer.compute_gradients(loss)
#     train = optimizer.apply_gradients(grads)
#
#     init = tf.global_variables_initializer()
#     sess = tf.Session()
#     sess.run(init)
#
# Then we can use the helper class as follows.
#
#     variables = ray.experimental.TensorFlowVariables(loss, sess)
#     weights = variables.get_weights()
#     variables.set_weights(weights)
#
# Note that there are analogous methods "variables.get_flat" and
# "variables.set_flat", which concatenate the weights as a single array insead
# of a dictionary.
#
# EXERCISE: Use the ray.experimental.TensorFlowVariables helper class to
# implement the set_weights and get_weights methods for the actor so that the
# driver can retrieve the weights from the actor and set new weights on the
# actor.
#
# EXERCISE: Additionally, use the actor methods to retrieve the neural net
# weights from all the actors, then average the weights, and then set the
# average on all of the actors.

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


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  # This actor contains a simple neural network.
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
      grads = optimizer.compute_gradients(self.loss)
      self.train = optimizer.apply_gradients(grads)

      init = tf.global_variables_initializer()
      self.sess = tf.Session()

      self.sess.run(init)

    def set_weights(self, weights):
      raise NotImplementedError

    def get_weights(self):
      raise NotImplementedError

  # Create a few actors with the model.
  actors = [SimpleModel() for _ in range(4)]

  # Get the weights from the actors.
  # EXERCISE: FILL THIS IN.
  raise Exception("Implement this.")

  # Average the weights.
  # EXERCISE: FILL THIS IN.
  raise Exception("Implement this.")

  # Set the average weights on the actors.
  # EXERCISE: FILL THIS IN.
  raise Exception("Implement this.")

  print("Success! The example ran to completion.")
