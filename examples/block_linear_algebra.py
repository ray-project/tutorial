from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy
import ray


# This class represents a distributed matrix with an array of object IDs, each
# of which corresponds to one block in the overall matrix.
class BlockMatrix(object):
  def __init__(self, shape, block_size=10):
    assert len(shape) == 2
    self.shape = shape
    self.block_size = block_size
    self.num_blocks = [int(np.ceil(a / self.block_size)) for a in self.shape]
    self.block_ids = np.empty(self.num_blocks, dtype=object)


# Note that we need to call ray.register_class so that we can pass BlockMatrix
# objects to remote functions and return them from remote functions.
ray.register_class(BlockMatrix)


# EXERCISE: Define a remote function which returns a block matrix of zeros.
@ray.remote
def zeros(shape):
  raise NotImplementedError


# EXERCISE: Define a remote function which returns a block matrix of ones.
@ray.remote
def ones(shape):
  raise NotImplementedError


# EXERCISE: Define a remote function which compares two block matrices "a" and
# "b" and returns true if
#
#    absolute(a - b) <= (atol + rtol * absolute(b))
#
# holds element-wise and false otherwise. For the equivalent numpy method, see
# https://docs.scipy.org/doc/numpy/reference/generated/numpy.allclose.html.
@ray.remote
def allclose(a, b, rtol=1e-05, atol=1e-08, equal_nan=False):
  raise NotImplementedError


# EXERCISE: Implement a remote function which multiplies two block matrices "a"
# and "b" and returns their product as a block matrix.
#
# You may find it helpful to define a helper function that takes a row of
# blocks from "a" and column of blocks from "b" and returns their product as a
# numpy array.
@ray.remote
def dot(a, b):
  raise NotImplementedError


# This is a helper method which takes a distributed matrix and assembles it
# into one big array on one machine. This is inefficient and only for testing
# purposes.
def assemble(a):
  result = np.zeros(a.shape)
  for i in a.num_blocks[0]:
    for j in a.num_blocks[1]:
      block_val = ray.get(a.block_ids[i, j])
      result[(i * a.block_size):((i + 1) * a.block_size),
             (j * a.block_size):((j + 1) * a.block_size)] = block_val
  return result


if __name__ == "__main__":
  ray.init()

  # Check that a matrix of zeros actually consists of zeros.
  x = zeros.remote([20, 33])
  assert np.allclose(assemble(ray.get(x)), np.zeros([20, 33]))

  # Check that a matrix of ones actually consists of ones.
  y = ones.remote([33, 15])
  assert np.allclose(assemble(ray.get(y)), np.zeros([33, 15]))

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
