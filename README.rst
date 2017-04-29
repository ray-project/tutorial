Ray Tutorial
============

Setup
-----

1. Install Ray by following the `Ray installation instructions`_. Verify that
   the following works.

  .. code-block:: bash

    python ray/test/runtest.py


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

**Exercise 2:** Use ``ray.wait`` to ignore stragglers.

**Exercise 3:** Use ``ray.wait`` to process tasks in the order that they finish.

**Exercise 4:** Pass object IDs into tasks to construct dependencies between
tasks.

**Exercise 5:** Call remote functions from within remote functions.

**Exercise 6:** Use actors to share state between tasks. See the documentation
on `using actors`_.

**Exercise 7:** Use actors to avoid multiple expensive initializations. See the
documentation on `using actors`_.

**Exercise 8:** Create a neural network inside of an actor.

**Exercise 9:** Extract neural network weights from an actor on one process, and
set them in another actor.

**Exercise 10:** Specify that an actor requires some GPUs.

.. _`using actors`: http://ray.readthedocs.io/en/latest/actors.html
