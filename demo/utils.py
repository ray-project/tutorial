from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tqdm
import ray

MOUNTAINCAR_DEFAULT_CONFIG = {
    "env": "MountainCarContinuous-v0",
    "actor_hiddens": [32, 64],
    "critic_hiddens": [64, 64],
    "n_step": 3,
    "model": {},
    "gamma": 0.99,
    "env_config": {},
    "exploration_should_anneal": True,
    "schedule_max_timesteps": 100000,
    "timesteps_per_iteration": 1000,
    "exploration_fraction": 0.4,
    "exploration_final_scale": 0.02,
    "exploration_ou_noise_scale": 0.75,
    "exploration_ou_theta": 0.15,
    "exploration_ou_sigma": 0.2,
    "target_network_update_freq": 0,
    "tau": 0.01,
    "buffer_size": 50000,
    "prioritized_replay": False,
    "prioritized_replay_alpha": 0.6,
    "prioritized_replay_beta": 0.4,
    "prioritized_replay_eps": 1.0e-06,
    "clip_rewards": False,
    "actor_lr": 0.001,
    "critic_lr": 0.001,
    "use_huber": False,
    "huber_threshold": 1.0,
    "l2_reg": 1.0e-05,
    "learning_starts": 1000,
    "sample_batch_size": 1,
    "train_batch_size": 64,
    "num_workers": 0,
    "num_gpus_per_worker": 0,
    "per_worker_exploration": False,
    "worker_side_prioritization": False,
    "evaluation_interval": 5,
    "evaluation_num_episodes": 10
}


def ray_get_with_progress_bar(object_ids):
    ready = []
    remaining = object_ids
    for _ in tqdm.tqdm(range(len(object_ids))):
        ready, remaining = ray.wait(remaining)
    return ray.get(ready)
