Ray Live Demo
=============

This demo can be run live while presenting to show Ray's capabilities.

## Instructions
1. Launch a Ray cluster on AWS with `ray up cluster_config.yaml`
    - To run locally, install the requirements with `pip install -r requirements.txt`
2. Connect to the head node
    - I recommend using SSH with port forwarding in order to use Jupyter, Ray Dashboard, and Tensorboard without compromising security
    - For example, `ssh -L 9999:127.0.0.1:8889 -L 9998:127.0.0.1:8080 -L 9997:127.0.0.1:6006 ubuntu@12.123.123.123` should map Jupyter to `127.0.0.1:9999`, Ray Dashboard to `127.0.0.1:9998` and Tensorboard to `127.0.0.1:9997`
2. Open the jupyter notebooks on the cluster and set the `CLUSTER_ADDRESS` parameter in `ray_api_demo.ipynb` and `rllib_demo.ipynb`
3. Also set links for Ray Dashboard and Tensorboard
4. Run the live-coding presentation with [rise](https://rise.readthedocs.io/)
    - Start a presentation with `Alt-r` or by pressing the button in the top right of the toolbar
    - Use `SpaceBar` to navigate to the next slide and `Shift-SpaceBar` to navigate to the previous slide
    - Use `Shift-Enter` to run the code in a cell
