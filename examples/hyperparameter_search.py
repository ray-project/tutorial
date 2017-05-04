# In this example, we will take a random hyperparameter optimization
# implementation and parallelize it.
#
# EXERCISE: Make train_cnn_and_compute_accuracy a remote function and train
# multiple models in parallel.
#
# EXERCISE: Make sure that you pass in object IDs for the data arguments
# (instead of numpy arrays) to train_cnn_and_compute_accuracy so that you avoid
# putting the data in the object store multiple times.
#
# EXERCISE: Using ray.wait, whenever one experiment finishes, print its
# accuracy and start a new experiment.
#
# EXERCISE: Use ray.experimental.TensorFlowVariables to extract the weights
# after training and return the weights from the remote function.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from ray_tutorial.mnist.mnist_model import cnn_setup


def get_batch(data, batch_index, batch_size):
  # This method currently drops data when num_data is not divisible by
  # batch_size.
  num_data = data.shape[0]
  num_batches = num_data // batch_size
  batch_index %= num_batches
  return data[(batch_index * batch_size):((batch_index + 1) * batch_size)]


# This is a function that takes a dictionary of hyperparameters as its first
# argument, constructs a neural network using those hyperparameters, trains the
# neural net, measures the validation accuracy, and returns the validation
# accuracy.
def train_cnn_and_compute_accuracy(params, steps, train_images, train_labels,
                                   validation_images, validation_labels):
  # Extract the hyperparameters from the params dictionary.
  learning_rate = params["learning_rate"]
  batch_size = params["batch_size"]
  keep = 1 - params["dropout"]
  stddev = params["stddev"]
  # Create the network and related variables.
  with tf.Graph().as_default():
    # Create the input placeholders for the network.
    x = tf.placeholder(tf.float32, shape=[None, 784])
    y = tf.placeholder(tf.float32, shape=[None, 10])
    keep_prob = tf.placeholder(tf.float32)
    # Create the network.
    train_step, accuracy, loss = cnn_setup(x, y, keep_prob, learning_rate,
                                           stddev)
    # Do the training and evaluation.
    with tf.Session() as sess:
      # Initialize the network weights.
      sess.run(tf.global_variables_initializer())
      # Do some steps of training.
      for i in range(1, steps + 1):
        # Fetch the next batch of data.
        image_batch = get_batch(train_images, i, batch_size)
        label_batch = get_batch(train_labels, i, batch_size)
        # Do one step of training.
        sess.run(train_step, feed_dict={x: image_batch, y: label_batch,
                                        keep_prob: keep})
      # Training is done, so compute the validation accuracy and the current
      # weights and return.
      totalacc = accuracy.eval(feed_dict={x: validation_images,
                                          y: validation_labels,
                                          keep_prob: 1.0})
  return float(totalacc)


if __name__ == "__main__":
  ray.init(redirect_output=True)

  # The number of sets of random hyperparameters to try.
  trials = 5
  # The number of training steps to use for each network.
  steps = 10

  # Load the mnist data and turn the data into remote objects.
  print("Downloading the MNIST dataset. This may take a minute.")
  mnist = input_data.read_data_sets("MNIST_data", one_hot=True)
  train_images = mnist.train.images
  train_labels = mnist.train.labels
  validation_images = mnist.validation.images
  validation_labels = mnist.validation.labels

  # A function for generating random hyperparameters.
  def generate_hyperparameters():
    return {"learning_rate": 10 ** np.random.uniform(-5, 5),
            "batch_size": np.random.randint(1, 100),
            "dropout": np.random.uniform(0, 1),
            "stddev": 10 ** np.random.uniform(-5, 5)}

  # Randomly generate some hyperparameters, and launch a task for each set.
  for i in range(trials):
    hyperparameters = generate_hyperparameters()
    accuracy = train_cnn_and_compute_accuracy(
        hyperparameters, steps, train_images, train_labels, validation_images,
        validation_labels)
    print("Accuracy is {}.".format(accuracy))
