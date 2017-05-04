from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import tensorflow as tf
import time

# The goal of this exercise is to show how to use GPUs with tasks and actors.

if __name__ == "__main__":
  # Start Ray, note that we pass in num_gpus=4. Ray will assume this machine
  # has 4 GPUs (even if it does not). When a task or actor requests a GPU, it
  # will be assigned a GPU ID from the set [0, 1, 2, 3]. It is then the
  # responsibility of the task or actor to make sure that it only uses that
  # specific GPU (e.g., by setting the CUDA_VISIBLE_DEVICES environment
  # variable).
  ray.init(num_cpus=4, num_gpus=4, redirect_output=True)

  # This is a class with a simple neural net.
  #
  # EXERCISE:
  #   1. Modify this class to make it an actor.
  #   2. Make the actor require a single GPU, and place the neural net on the
  #      GPU. This should still work even if you run this on a machine with no
  #      GPUs because we set allow_soft_placement=True below. To get this to
  #      work on a machine with multiple GPUs, you will probably need to set
  #      the environment variable CUDA_VISIBLE_DEVICES properly (before you
  #      create the TensorFlow session object).
  #   3. Create one actor for each GPU, and verify that they are placed on
  #      different GPUs.
  class Network(object):
    def __init__(self, x, y):
      with tf.device("/cpu:0"):
        # NOTE: We create each network inside a separate graph. Doing this can
        # be critical. In particular
        with tf.Graph().as_default():
          # Define the inputs.
          x_data = tf.constant(x, dtype=tf.float32)
          y_data = tf.constant(y, dtype=tf.float32)
          # Define the weights and computation.
          w = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
          b = tf.Variable(tf.zeros([1]))
          y = w * x_data + b
          # Define the loss.
          self.loss = tf.reduce_mean(tf.square(y - y_data))
          optimizer = tf.train.GradientDescentOptimizer(0.5)
          self.grads = optimizer.compute_gradients(self.loss)
          self.train = optimizer.apply_gradients(self.grads)
          # Define the weight initializer and session.
          init = tf.global_variables_initializer()
          # By setting allow_soft_placement=True, we allow this code to run
          # even if the machine has no GPUs.
          config = tf.ConfigProto(allow_soft_placement=True)
          self.sess = tf.Session(config=config)
          # Additional code for setting and getting the weights
          self.variables = ray.experimental.TensorFlowVariables(self.loss,
                                                                self.sess)
          # Return all of the data needed to use the network.
          self.sess.run(init)

    # Define a remote function that trains the network for one step and returns
    # the new weights.
    def step(self, weights):
      # Set the weights in the network.
      self.variables.set_weights(weights)
      # Do one step of training. We only need the actual gradients so we filter
      # over the list.
      actual_grads = self.sess.run([grad[0] for grad in self.grads])
      return actual_grads

    def get_weights(self):
      return self.variables.get_weights()

  num_data = 1000
  x_data = np.random.rand(num_data)
  y_data = x_data * 0.1 + 0.3

  # EXERCISE: Note that when you make Network an actor and you pass x_data and
  # y_data (which are both numpy arrays) into the Network constructor, every
  # time you create a new Network actor, x_data and y_data will be serialized
  # and put in the object store. In order to place them in the object store
  # only once, you can use call ray.put on the objects and pass the resulting
  # object IDs into the Network constructor.
  actors = [Network(x_data, y_data) for _ in range(4)]

  # Get the weights of the first actor.
  weights = actors[0].get_weights()

  # Do a training step on each actor.
  [actor.step(weights) for actor in actors]
