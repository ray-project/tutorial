Tune Tutorial
-------------

.. image:: ./tune.png

Tuning hyperparameters is often the most expensive part of the machine learning workflow. Tune is built to address this, demonstrating an efficient and scalable solution for this pain point.

**Code**: https://github.com/ray-project/ray/tree/master/python/ray/tune

**Examples**: https://github.com/ray-project/ray/tree/master/python/ray/tune/examples

**Documentation**: http://ray.readthedocs.io/en/latest/tune.html

**Mailing List** https://groups.google.com/forum/#!forum/ray-dev


Notebooks
---------

1. exercise_1_basics.ipynb covers basics of using Tune - creating your first training function and using Tune. This tutorial uses Keras.
2. exercise_2_optimize.ipynb covers Search algorithms and Trial Schedulers. This tutorial uses PyTorch.


Concepts that are generally useful but have not been covered: 

1. Using PBT
2. Creating a Trainable with save and restore functions and checkpointing
3. Distributed execution on a larger cluster

Please open an issue if you have any questions or identify any issues. All suggestions and contributions welcome!
