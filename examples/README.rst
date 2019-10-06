Running Ray Tutorial Examples with Projects
===========================================

You can run the tutorial examples with Ray projects. To do so
you need to run the following commands, the second one in this
directory:

.. code-block:: bash

    pip install any
    any project create


Starting the Tutorial
---------------------

You can start the tutorial with

.. code-block:: bash

    any session start -y tutorial


After the session is started, it will print an URL like

.. cod-block::

    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://localhost:8889/?token=0a30613eb5e22c2e30ab76811c2a23551c1535c3a10ba971&token=0a30613eb5e22c2e30ab76811c2a23551c1535c3a10ba971


that you can use to access the notebook.


Stopping the Tutorial
---------------------

The tutorial session can be stopped with

.. code-block:: bash

    any session stop
