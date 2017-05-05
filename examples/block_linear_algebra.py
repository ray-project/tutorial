# EXERCISE: Implement all of the missing functions below. This script should
# run without raising any exceptions.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray


# This class represents a distributed matrix with an array of object IDs, each
# of which corresponds to one block in the overall matrix.
class BlockMatrix(object):
  def __init__(self, shape, block_size=10):
    assert len(shape) == 2
    self.shape = shape
    self.block_size = block_size
    self.num_blocks = [int(np.ceil(a / self.block_size)) for a in self.shape]
    # The field "block_ids" will be a numpy array of object IDs, where each
    # object ID refers to a numpy array.
    self.block_ids = np.empty(self.num_blocks, dtype=object)


# Note that we need to call ray.register_class so that we can pass BlockMatrix
# objects to remote functions and return them from remote functions.
ray.register_class(BlockMatrix)


# This is a helper function which creates an array of zeros.
@ray.remote
def zeros_helper(shape):
  return np.zeros(shape)


# EXERCISE: Define a remote function which returns a BlockMatrix of zeros. You
# can assume that len(shape) == 2. You can do this as follows.
#   - First call the BlockMatrix constructor with the appropriate shape.
#   - Then call "zeros_helper" to create an object ID for each entry of
#     the "block_ids" field of the BlockMatrix.
#
# NOTE: You could call "zeros_helper" once for every block in the BlockMatrix,
# but since object IDs refer to immutable objects, if you create two matrices
# of zeros with the same shape, then you could choose to reuse the same object
# ID for both of them.
#
# EXERCISE: Implement this method more efficiently by reusing object IDs for
# the blocks that have shape block_size x block_size.
@ray.remote
def zeros(shape):
  raise NotImplementedError


# EXERCISE: Define a remote function which returns a BlockMatrix of ones.
#
# You may find it helpful to implement a helper remote function which wraps
# np.ones and then call that multiple times inside of this function.
@ray.remote
def ones(shape):
  raise NotImplementedError


# EXERCISE: Define a remote function which compares two BlockMatrix objects "a"
# and "b" and returns true if
#
#    absolute(a - b) <= (atol + rtol * absolute(b))
#
# holds element-wise and false otherwise. For the equivalent numpy method, see
# https://docs.scipy.org/doc/numpy/reference/generated/numpy.allclose.html.
@ray.remote
def allclose(a, b, rtol=1e-05, atol=1e-08, equal_nan=False):
  raise NotImplementedError


# EXERCISE: Implement a remote function which multiplies two BlockMatrix
# objects "a" and "b" and returns their product as a BlockMatrix.
#
# You may find it helpful to define a helper function that takes a row of
# blocks from "a" and column of blocks from "b" and returns their product as a
# numpy array.
#
# Note that to make a Python function take a variable number of arguments, you
# can use the following signature.
#
#     def f(*ids):
#       print(ids)
#
# And then you can call f as follows.
#
#     f(*[1, 2, 3])
#
# This will print "[1, 2, 3]".
#
# For Ray, this trick matters because object ID arguments will be fetched and
# the corresponding Python objects will be passed into the remote function.
# However, if an object ID is passed in inside of a list (or other structure),
# its value will not be fetched and it will be passed in unchanged.
@ray.remote
def dot(a, b):
  raise NotImplementedError


# This is a helper method which takes a distributed matrix and assembles it
# into one big array on one machine. This is inefficient and only for testing
# purposes.
def assemble(a):
  result = np.zeros(a.shape)
  for i in range(a.num_blocks[0]):
    for j in range(a.num_blocks[1]):
      block_val = ray.get(a.block_ids[i, j])
      result[(i * a.block_size):((i + 1) * a.block_size),
             (j * a.block_size):((j + 1) * a.block_size)] = block_val
  return result


if __name__ == "__main__":
  ray.init(redirect_output=True)

  # Check that a matrix of zeros actually consists of zeros.
  x = zeros.remote([20, 33])
  assert np.allclose(assemble(ray.get(x)), np.zeros([20, 33]))

  print("\nSuccessfully created a BlockMatrix of zeros!\n")

  # Check that a matrix of ones actually consists of ones.
  y = ones.remote([33, 15])
  assert np.allclose(assemble(ray.get(y)), np.ones([33, 15]))

  print("\nSuccessfully created a BlockMatrix of ones!\n")

  # Check that the product of x and y is a matrix of all zeros.
  assert ray.get(allclose.remote(dot.remote(x, y), zeros.remote([20, 15])))

  # Check that the dot function works.
  a = ones.remote([17, 20])
  b = ones.remote([20, 30])
  c = dot.remote(a, b)
  a_val = assemble(ray.get(a))
  b_val = assemble(ray.get(b))
  c_val = assemble(ray.get(c))
  assert np.allclose(np.dot(a_val, b_val), c_val)

  print("\nSuccessfully multiplied two BlockMatrix objects!\n")

  # Check the efficiency of the zeros implementation.
  w = zeros.remote([50, 50])
  w_val = ray.get(w)
  num_unique_ids = len(set(list(w_val.block_ids.reshape(5 * 5))))
  assert num_unique_ids == 1, ("The implementation of zeros can be made more "
                               "efficient.")
