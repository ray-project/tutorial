from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import argparse
import gym

from ray.rllib.utils.policy_client import PolicyClient

parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-train", action="store_true", help="Whether to disable training.")
parser.add_argument(
    "--off-policy",
    action="store_true",
    help="Whether to take random instead of on-policy actions.")


if __name__ == "__main__":
    args = parser.parse_args()
    import pong_py
    env = pong_py.PongJSEnv()
    client = PolicyClient("http://localhost:8900")

    eid = client.start_episode(training_enabled=not args.no_train)
    obs = env.reset()
    rewards = 0
    episode = []
    f = open("out.txt", "w")

    while True:
        if args.off_policy:
            action = env.action_space.sample()
            client.log_action(eid, obs, action)
        else:
            action = client.get_action(eid, obs)
        next_obs, reward, done, info = env.step(action)
        episode.append({
            "obs": obs.tolist(),
            "action": float(action),
            "reward": reward,
        })
        obs = next_obs
        rewards += reward
        client.log_returns(eid, reward, info=info)
        if done:
            print("Total reward:", rewards)
            f.write(json.dumps(episode))
            f.write("\n")
            f.flush()
            rewards = 0
            client.end_episode(eid, obs)
            obs = env.reset()
            eid = client.start_episode(training_enabled=not args.no_train)
