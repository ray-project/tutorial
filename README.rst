Ray Tutorial
============

Setup
-----

1. Install Ray by following the `Ray installation instructions`_.

2. Clone the tutorial repository with

  .. code-block:: bash

    git clone https://github.com/ray-project/tutorial.git

3. Install the tutorial package with

  .. code-block:: bash

    cd ray-tutorial
    python setup.py install

.. _`Ray installation instructions`: http://ray.readthedocs.io/en/latest/index.html

4. Install the following additional dependencies.

  .. code-block:: bash

    pip install tensorflow
    pip install gym[atari]

  Verify that you can run ``import tensorflow`` and ``import gym`` in a Python
  interpreter.


Exercises
---------

**Exercise 1:** Define a remote function, and execute multiple remote functions
in parallel.

**Exercise 2:** Use ``ray.wait`` to process tasks in the order that they finish.

**Exercise 3:** Pass object IDs into tasks to construct dependencies between
tasks.

**Exercise 4:** Call remote functions from within remote functions.

**Exercise 5:** Create a neural network inside of an actor.

**Exercise 6:** Extract neural network weights from an actor on one process, and
set them in another actor.
