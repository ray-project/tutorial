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
