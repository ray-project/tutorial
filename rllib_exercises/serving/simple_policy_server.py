from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

from gym import spaces
import numpy as np

import ray
from ray.rllib.agents.dqn import DQNAgent
from ray.rllib.agents.pg import PGAgent
from ray.rllib.env.serving_env import ServingEnv
from ray.rllib.utils.policy_server import PolicyServer
from ray.tune.logger import pretty_print
from ray.tune.registry import register_env

SERVER_ADDRESS = "localhost"
SERVER_PORT = 8900

parser = argparse.ArgumentParser()
parser.add_argument("--action-size", type=int, required=True)
parser.add_argument("--observation-size", type=int, required=True)
parser.add_argument("--checkpoint-file", type=str, required=True)
parser.add_argument("--run", type=str, required=True)


class SimpleServing(ServingEnv):
    def __init__(self, config):
        ServingEnv.__init__(
            self, spaces.Discrete(config["action_size"]),
            spaces.Box(
                low=-10, high=10,
                shape=(config["observation_size"],),
                dtype=np.float32))

    def run(self):
        print("Starting policy server at {}:{}".format(SERVER_ADDRESS,
                                                       SERVER_PORT))
        server = PolicyServer(self, SERVER_ADDRESS, SERVER_PORT)
        server.serve_forever()


if __name__ == "__main__":
    args = parser.parse_args()
    ray.init()
    register_env("srv", lambda config: SimpleServing(config))

    if args.run == "DQN":
        agent = DQNAgent(
            env="srv",
            config={
                # Use a single process to avoid needing a load balancer
                "num_workers": 0,
                # Configure the agent to run short iterations for debugging
                "exploration_fraction": 0.01,
                "learning_starts": 100,
                "timesteps_per_iteration": 200,
                "env_config": {
                    "observation_size": args.observation_size,
                    "action_size": args.action_size,
                },
            })
    elif args.run == "PG":
        agent = PGAgent(
            env="srv",
            config={
                "num_workers": 0,
                "env_config": {
                    "observation_size": args.observation_size,
                    "action_size": args.action_size,
                },
            })

    # Attempt to restore from checkpoint if possible.
    if os.path.exists(args.checkpoint_file):
        checkpoint_file = open(args.checkpoint_file).read()
        print("Restoring from checkpoint path", checkpoint_file)
        agent.restore(checkpoint_file)

    # Serving and training loop
    while True:
        print(pretty_print(agent.train()))
        checkpoint_file = agent.save()
        print("Last checkpoint", checkpoint_file)
        with open(args.checkpoint_file, "w") as f:
            f.write(checkpoint_file)
