# The goal of this exercise is to develop some intuition for what kinds of
# objects Ray can serialize and deserialize efficiently, and what kinds are
# handled inefficiently.
#
# HIGH-LEVEL TAKEAWAY: Whenever possible, use numpy arrays.
#
# You can serialize a Python object and place it in the object store with
# ray.put. You can then retrieve it and deserialize it with ray.get. This
# should work out of the box with all primitive data types (e.g., ints, floats,
# string, lists, tuples, dictionaries, and numpy arrays). However, an extra
# line is needed to handle custom Python objects or more complex objects.
#
# For example, if you define a custom class, then in order to pass it to a
# remote function, you need to call ray.register_class.
#
#     class Foo(object):
#       def __init__(self, a, b):
#         self.a = a
#         self.b = b
#
#     ray.put(Foo(1, 2))  # This raises an exception.
#
#     ray.register_class(Foo)  # This tells Ray to serialize objects of type
#                              # "Foo" by turning them into a dictionary of
#                              # their fields, e.g., {"a": 1, "b": 2}.
#     ray.get(ray.put(Foo(1, 2)))  # This should work.
#
# Not everything can be serialized by unpacking its fields into a dictionary,
# so for those objects, we can fall back to pickle. E.g.,
#
#     ray.register_class(t, pickle=True)  # This tells Ray to serialize objects
#                                         # of type t with pickle (actually we
#                                         # use cloudpickle under the hood).
#
# NOTE: This is one of the uglier parts of the API. We can make more things
# work out of the box by falling back to pickle, but the danger is that small
# changs to application code could cause a change in the way serialization is
# done (from our custom serialization using Apache Arrow to pickle), which
# could lead to a big performance hit without any explanation.
#
# EXERCISE: See if you can make the following code run by calling
# ray.register_class in the appropriate places. NOTE: It is probably simpler to
# play around with this in an ipython interpreter than to repeatedly run this
# script. Also, if you want to drop into an the interpreter in the middle of
# this script, you can add the following lines.
#
#     import IPython
#     IPython.embed()

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import ray
import time


if __name__ == "__main__":
  ray.init(num_cpus=4, redirect_output=True)

  class Foo(object):
    def __init__(self, x):
      self.x = x

  # By default, Ray doesn't know how to serialize Foo objects. Make this work.
  result = ray.get(ray.put(Foo(1)))
  assert result.x == 1

  class Bar(object):
    def __init__(self, a, b):
      self.a = a
      self.b = b
      self.c = np.ones((a, b))

  class Qux(object):
    def __init__(self, a, b):
      self.bar = Bar(a, b)

  # By default, Ray doesn't know how to serialize Qux objects. Make the line
  # below work. NOTE: if Ray falls back to pickling the Qux object, then Ray
  # will not be able to efficiently handle the large numpy array inside.
  # Compare the performance difference with and without pickling.
  result = ray.get(ray.put(Qux(1000, 10000)))
  assert result.bar.a == 1000
  assert result.bar.b == 10000
  assert np.allclose(result.bar.c, np.ones((1000, 10000)))

  print("Success! The example ran to completion.")
