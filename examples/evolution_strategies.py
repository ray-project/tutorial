# Code in this file is copied and adapted from
# https://github.com/openai/evolution-strategies-starter.
#
# This code creates a set of "Worker" objects with
#
#       workers = [Worker(...) for _ in range(num_workers)]
#
# It then enters an infinite loop which alternates between doing rollouts with
#
#     results = [worker.do_rollouts(...) for worker in workers]
#
# and updating the policy with
#
#     optimizer.update(...)
#
# where the update to the policy is computed using "results".
#
# EXERCISE: Make the "Worker" objects actors so that they are started as new
# processes.
#
# EXERCISE: Do the rollouts in parallel to speed up the computation. Note that
# we are currently only starting two workers, so the opportunity for
# parallelism will depend on the number of workers.
#
# EXERCISE: This code uses a large numpy array of noise that is shared between
# the workers. This array is created by the function "create_shared_noise".
# Make "create_shared_noise" a remote function so that the noise object is put
# in shared memory and shared between all of the worker processes (so each
# worker does not create its own copy of the array). Note that the array of
# noise is fairly large and takes a little while to create.
#
# Note, the code in this example was tuned for the Humanoid-v1 gym environment.
# Here we're running it on Pendulum-v0 for simplicity, but it works best on
# the Humanoid environment.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple
import gym
import numpy as np
import ray
import tensorflow as tf
import time

from ray_tutorial.evolution_strategies import (optimizers, policies,
                                               tabular_logger, tf_util, utils)


Config = namedtuple("Config", [
    "l2coeff", "noise_stdev", "episodes_per_batch", "timesteps_per_batch",
    "calc_obstat_prob", "eval_prob", "snapshot_freq", "return_proc_mode",
    "episode_cutoff_mode"
])

Result = namedtuple("Result", [
    "noise_inds_n", "returns_n2", "sign_returns_n2", "lengths_n2",
    "eval_return", "eval_length", "ob_sum", "ob_sumsq", "ob_count"
])


def create_shared_noise():
  """Create a large array of noise to be shared by all workers."""
  seed = 123
  count = 250000000
  noise = np.random.RandomState(seed).randn(count).astype(np.float32)
  return noise


class SharedNoiseTable(object):
  def __init__(self, noise):
    self.noise = noise
    assert self.noise.dtype == np.float32

  def get(self, i, dim):
    return self.noise[i:i + dim]

  def sample_index(self, stream, dim):
    return stream.randint(0, len(self.noise) - dim + 1)


class Worker(object):
  def __init__(self, config, policy_params, env_name, noise,
               min_task_runtime=0.2):
    self.min_task_runtime = min_task_runtime
    self.config = config
    self.policy_params = policy_params
    self.noise = SharedNoiseTable(noise)

    self.env = gym.make(env_name)
    self.sess = utils.make_session(single_threaded=True)
    self.policy = policies.MujocoPolicy(self.env.observation_space,
                                        self.env.action_space,
                                        **policy_params)
    tf_util.initialize()

    self.rs = np.random.RandomState()

    assert self.policy.needs_ob_stat == (self.config.calc_obstat_prob != 0)

  def rollout_and_update_ob_stat(self, timestep_limit, task_ob_stat):
    if (self.policy.needs_ob_stat and self.config.calc_obstat_prob != 0 and
            self.rs.rand() < self.config.calc_obstat_prob):
      rollout_rews, rollout_len, obs = self.policy.rollout(
          self.env, timestep_limit=timestep_limit, save_obs=True,
          random_stream=self.rs)
      task_ob_stat.increment(obs.sum(axis=0), np.square(obs).sum(axis=0),
                             len(obs))
    else:
      rollout_rews, rollout_len = self.policy.rollout(
          self.env, timestep_limit=timestep_limit, random_stream=self.rs)
    return rollout_rews, rollout_len

  def do_rollouts(self, params, ob_mean, ob_std, timestep_limit):
    # Set the network weights.
    self.policy.set_trainable_flat(params)

    if self.policy.needs_ob_stat:
      self.policy.set_ob_stat(ob_mean, ob_std)

    if self.rs.rand() < self.config.eval_prob:
      print("In this case, the reference implementation uses no noise in "
            "order to evaluate the policy. We're ignoring that.")

    noise_inds, returns, sign_returns, lengths = [], [], [], []
    task_ob_stat = utils.RunningStat(self.env.observation_space.shape, eps=0)

    # Perform some rollouts with noise.
    while (len(noise_inds) == 0 or
           time.time() - task_tstart < self.min_task_runtime):
      noise_idx = self.noise.sample_index(self.rs, self.policy.num_params)
      v = self.config.noise_stdev * self.noise.get(noise_idx,
                                                   self.policy.num_params)

      # These two sampling steps could be done in parallel on different actors
      # letting us update twice as frequently.
      self.policy.set_trainable_flat(params + v)
      rews_pos, len_pos = self.rollout_and_update_ob_stat(timestep_limit,
                                                          task_ob_stat)

      self.policy.set_trainable_flat(params - v)
      rews_neg, len_neg = self.rollout_and_update_ob_stat(timestep_limit,
                                                          task_ob_stat)

      noise_inds.append(noise_idx)
      returns.append([rews_pos.sum(), rews_neg.sum()])
      sign_returns.append([np.sign(rews_pos).sum(), np.sign(rews_neg).sum()])
      lengths.append([len_pos, len_neg])

      return Result(
        noise_inds_n=np.array(noise_inds),
        returns_n2=np.array(returns, dtype=np.float32),
        sign_returns_n2=np.array(sign_returns, dtype=np.float32),
        lengths_n2=np.array(lengths, dtype=np.int32),
        eval_return=None,
        eval_length=None,
        ob_sum=(None if task_ob_stat.count == 0 else task_ob_stat.sum),
        ob_sumsq=(None if task_ob_stat.count == 0 else task_ob_stat.sumsq),
        ob_count=task_ob_stat.count)


if __name__ == "__main__":
  num_workers = 2
  env_name = "Pendulum-v0"
  stepsize = 0.01

  ray.init(redirect_output=True)

  config = Config(l2coeff=0.005,
                  noise_stdev=0.02,
                  episodes_per_batch=10000,
                  timesteps_per_batch=100000,
                  calc_obstat_prob=0.01,
                  eval_prob=0.003,
                  snapshot_freq=20,
                  return_proc_mode="centered_rank",
                  episode_cutoff_mode="env_default")

  policy_params = {
    "ac_bins": "continuous:",
    "ac_noise_std": 0.01,
    "nonlin_type": "tanh",
    "hidden_dims": [256, 256],
    "connection_type": "ff"
  }

  # Create the shared noise table.
  print("Creating shared noise table.")
  noise_array = create_shared_noise()
  noise = SharedNoiseTable(noise_array)

  # Create the workers.
  print("Creating workers.")
  workers = [Worker(config, policy_params, env_name, noise_array)
             for _ in range(num_workers)]

  env = gym.make(env_name)
  sess = utils.make_session(single_threaded=False)
  policy = policies.MujocoPolicy(env.observation_space, env.action_space,
                                 **policy_params)
  tf_util.initialize()
  optimizer = optimizers.Adam(policy, stepsize)

  ob_stat = utils.RunningStat(env.observation_space.shape, eps=1e-2)

  episodes_so_far = 0
  timesteps_so_far = 0
  tstart = time.time()

  while True:
    step_tstart = time.time()
    theta = policy.get_trainable_flat()
    assert theta.dtype == np.float32

    # These rollouts could be done in parallel.
    results = [worker.do_rollouts(
                   theta,
                   ob_stat.mean if policy.needs_ob_stat else None,
                   ob_stat.std if policy.needs_ob_stat else None,
                   None)
               for worker in workers]

    curr_task_results, eval_rets, eval_lens = [], [], []
    num_results_skipped = 0
    num_episodes_popped = 0
    num_timesteps_popped = 0
    ob_count_this_batch = 0
    # Loop over the results
    for result in results:
      assert result.eval_length is None, "We aren't doing eval rollouts."
      assert result.noise_inds_n.ndim == 1
      assert result.returns_n2.shape == (len(result.noise_inds_n), 2)
      assert result.lengths_n2.shape == (len(result.noise_inds_n), 2)
      assert result.returns_n2.dtype == np.float32

      result_num_eps = result.lengths_n2.size
      result_num_timesteps = result.lengths_n2.sum()
      episodes_so_far += result_num_eps
      timesteps_so_far += result_num_timesteps

      curr_task_results.append(result)
      num_episodes_popped += result_num_eps
      num_timesteps_popped += result_num_timesteps
      # Update ob stats.
      if policy.needs_ob_stat and result.ob_count > 0:
        ob_stat.increment(result.ob_sum, result.ob_sumsq, result.ob_count)
        ob_count_this_batch += result.ob_count

    # Assemble the results.
    noise_inds_n = np.concatenate([r.noise_inds_n for
                                   r in curr_task_results])
    returns_n2 = np.concatenate([r.returns_n2 for r in curr_task_results])
    lengths_n2 = np.concatenate([r.lengths_n2 for r in curr_task_results])
    assert noise_inds_n.shape[0] == returns_n2.shape[0] == lengths_n2.shape[0]
    # Process the returns.
    assert config.return_proc_mode == "centered_rank"
    proc_returns_n2 = utils.compute_centered_ranks(returns_n2)

    # Compute and take a step.
    g, count = utils.batched_weighted_sum(
        proc_returns_n2[:, 0] - proc_returns_n2[:, 1],
        (noise.get(idx, policy.num_params) for idx in noise_inds_n),
        batch_size=500)
    g /= returns_n2.size
    assert (g.shape == (policy.num_params,) and g.dtype == np.float32 and
            count == len(noise_inds_n))
    update_ratio = optimizer.update(-g + config.l2coeff * theta)

    step_tend = time.time()

    # Log some statistics.
    tabular_logger.record_tabular("EpRewMean", returns_n2.mean())
    tabular_logger.record_tabular("EpRewStd", returns_n2.std())
    tabular_logger.record_tabular("EpLenMean", lengths_n2.mean())

    tabular_logger.record_tabular("Norm", float(np.square(
        policy.get_trainable_flat()).sum()))
    tabular_logger.record_tabular("GradNorm", float(np.square(g).sum()))
    tabular_logger.record_tabular("UpdateRatio", float(update_ratio))

    tabular_logger.record_tabular("EpisodesThisIter", lengths_n2.size)
    tabular_logger.record_tabular("EpisodesSoFar", episodes_so_far)
    tabular_logger.record_tabular("TimestepsThisIter", lengths_n2.sum())
    tabular_logger.record_tabular("TimestepsSoFar", timesteps_so_far)

    tabular_logger.record_tabular("ObCount", ob_count_this_batch)

    tabular_logger.record_tabular("TimeElapsedThisIter",
                                  step_tend - step_tstart)
    tabular_logger.record_tabular("TimeElapsed", step_tend - tstart)
    tabular_logger.dump_tabular()
