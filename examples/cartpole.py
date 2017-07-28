import time

import numpy as np
import gym
import tensorflow as tf
import tensorflow.contrib.slim as slim

n_obs = 4              # dimensionality of observations
n_h = 256              # number of hidden layer neurons
n_actions = 2          # number of available actions
learning_rate = 5e-4   # how rapidly to update parameters
gamma = .99            # reward discount factor

env = gym.make("CartPole-v0")
observation = env.reset()
observations, rewards, labels = [], [], []
reward_sum = 0
reward_sums = []
episode_number = 0
num_timesteps = 0

def make_policy(observation_placeholder):
    hidden = slim.fully_connected(observation_placeholder, n_h)
    log_probability = slim.fully_connected(hidden, n_actions, activation_fn=None, weights_initializer=tf.truncated_normal_initializer(0.001))
    return tf.nn.softmax(log_probability)

def discounted_normalized_rewards(r):
  """Take 1D float array of rewards and compute normalized discounted reward."""
  result = np.zeros_like(r)
  running_sum = 0
  for t in reversed(range(0, r.size)):
    running_sum = running_sum * gamma + r[t]
    result[t] = running_sum
  return (result - np.mean(result)) / np.std(result)

input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])
input_probability = tf.placeholder(dtype=tf.float32, shape=[None, n_actions])
input_reward = tf.placeholder(dtype=tf.float32, shape=[None,1])

# The policy network.
action_probability = make_policy(input_observation)

loss = tf.nn.l2_loss(input_probability - action_probability)
optimizer = tf.train.AdamOptimizer(learning_rate)
train_op = optimizer.minimize(loss, grad_loss=input_reward)

# Create TensorFlow session and initialize variables.
sess = tf.InteractiveSession()
tf.initialize_all_variables().run()

num_timesteps = 0

start_time = time.time()

# Training loop
while True:

    # stochastically sample a policy from the network
    probability = sess.run(action_probability, {input_observation: observation[np.newaxis, :]})[0,:]

    action = np.random.choice(n_actions, p = probability)
    label = np.zeros_like(probability) ; label[action] = 1
    observations.append(observation)
    labels.append(label)

    observation, reward, done, info = env.step(action)
    reward_sum += reward

    rewards.append(reward)

    if done:
        timesteps = len(rewards)

        if (num_timesteps + timesteps) // 5000 > num_timesteps // 5000:
            print('time: {:4.1f}, timesteps: {:7.0f}, reward: {:7.3f}'.format(
                time.time() - start_time, num_timesteps + timesteps, np.mean(reward_sums)))

        num_timesteps += timesteps

        feed = {input_observation: np.vstack(observations),
                input_reward: discounted_normalized_rewards(np.vstack(rewards)),
                input_probability: np.vstack(labels)}
        sess.run(train_op, feed)
        observations, rewards, labels = [], [], [] # Reset history.

        episode_number += 1
        observation = env.reset()
        reward_sums.append(reward_sum)
        reward_sum = 0
