Ray Tutorial
============

Setup
-----

1. Make sure you have Python installed (we recommend using the `Anaconda Python
   distribution`_). Ray works with both Python 2 and Python 3. If you are unsure
   which to use, then use Python 3.

2. **Install Jupyter** with ``pip install jupyter``. Verify that you can start
   a Jupyter notebook with the command ``jupyter-notebook``.

3. **Install Ray** by running ``pip install -U ray``. Verify that you can run

    .. code-block:: bash

      import ray
      ray.init()

   in a Python interpreter.

4. Clone the tutorial repository with

    .. code-block:: bash

      git clone https://github.com/ray-project/tutorial.git

5. Install the following additional dependencies.

    .. code-block:: bash

      pip install tensorflow
      pip install gym
      pip install scipy
      pip install opencv-python
      pip install bokeh
      pip install ipywidgets==6.0.0

   Verify that you can run ``import tensorflow`` and ``import gym`` in a Python
   interpreter.

   **Note:** If you have trouble installing these Python modules, note that
   almost all of the exercises can be done without them.

Exercises
---------

Each file ``exercises/exercise*.ipynb`` is a separate exercise. They can be
opened in a Jupyter notebook by running the following commands.

.. code-block:: bash

  cd tutorial/exercises
  jupyter-notebook

If it asks for a password, just hit enter.

Instructions are written in each file. To do each exercise, first run all of
the cells in the Jupyter notebook. Then modify the ones that need to be modified
in order to prevent any exceptions from being raised. Throughout these
exercises, you may find the `Ray documentation`_ helpful.

**Exercise 1:** Define a remote function, and execute multiple remote functions
in parallel.

**Exercise 2:** Execute remote functions in parallel with some dependencies.

**Exercise 3:** Pass object IDs into tasks to construct dependencies between
tasks.

**Exercise 4:** Call remote functions from within remote functions.

**Exercise 5:** Use ``ray.wait`` to ignore stragglers. See the
`documentation for wait`_.

**Exercise 6:** Use ``ray.wait`` to process tasks in the order that they finish.
See the `documentation for wait`_.

**Exercise 7:** Use actors to share state between tasks. See the documentation
on `using actors`_.

**Exercise 8:** Pass actor handles to tasks so that multiple tasks can invoke
methods on the same actor.

**Exercise 9:** Use ``ray.put`` to avoid serializing and copying the same
object into shared memory multiple times.

**Exercise 10:** Specify that an actor requires some GPUs. For a complete
example that does something similar, you may want to see the `ResNet example`_.

**Exercise 11:** Specify that a remote function requires certain custom
resources. See the documentation on `custom resources`_.

**Exercise 12:** Extract neural network weights from an actor on one process,
and set them in another actor. You may want to read the documentation on
`using Ray with TensorFlow`_.

.. _`Anaconda Python distribution`: https://www.continuum.io/downloads
.. _`Ray documentation`: http://ray.readthedocs.io/en/latest/?badge=latest
.. _`documentation for wait`: http://ray.readthedocs.io/en/latest/api.html#waiting-for-a-subset-of-tasks-to-finish.
.. _`using actors`: http://ray.readthedocs.io/en/latest/actors.html
.. _`using Ray with TensorFlow`: http://ray.readthedocs.io/en/latest/using-ray-with-tensorflow.html
.. _`ResNet example`: http://ray.readthedocs.io/en/latest/example-resnet.html
.. _`custom resources`: http://ray.readthedocs.io/en/latest/resources.html#custom-resources


More In-Depth Examples
----------------------

**Sharded Parameter Server:** This exercise involves implementing a parameter
server as a Ray actor, implementing a simple asynchronous distributed training
algorithm, and sharding the parameter server to improve throughput.

**Speed Up Pandas:** This exercise involves using `Modin`_ to speed up your
pandas workloads.

**MapReduce:** This exercise shows how to implement a toy version of the
MapReduce system on top of Ray.

.. _`Modin`: https://modin.readthedocs.io/en/latest/

RL Exercises
------------

Each file in ``rl_exercises/rl_exercise*.ipynb`` is a separate Jupyter notebook.
These exercises should be done in order. They can be opened in a Jupyter
notebook by running the following commands.

.. code-block:: bash

  cd tutorial/rl_exercises
  jupyter-notebook
