import numpy as np
import gym
import tensorflow as tf
import tensorflow.contrib.slim as slim

n_obs = 4              # dimensionality of observations
n_h = 128              # number of hidden layer neurons
n_actions = 2          # number of available actions
learning_rate = 1e-2   # how rapidly to update parameters
gamma = .9             # reward discount factor

env = gym.make("CartPole-v1")
observation = env.reset()
observations, rewards, labels = [], [], []
running_reward = 10    # worst case is ~10 for cartpole
reward_sum = 0
episode_number = 0
max_steps = 1000

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
hidden = slim.fully_connected(input_observation, n_h)
log_probability = slim.fully_connected(hidden, n_actions, activation_fn=None)
action_probability = tf.nn.softmax(log_probability)

loss = tf.nn.l2_loss(input_probability - action_probability)
optimizer = tf.train.AdamOptimizer(learning_rate)
train_op = optimizer.minimize(loss, grad_loss=input_reward)

# Create TensorFlow session and initialize variables.
sess = tf.InteractiveSession()
tf.initialize_all_variables().run()

# Tralining loop
while episode_number <= max_steps:

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
        running_reward = running_reward * 0.99 + reward_sum * 0.01

        feed = {input_observation: np.vstack(observations),
                input_reward: discounted_normalized_rewards(np.vstack(rewards)),
                input_probability: np.vstack(labels)}
        sess.run(train_op, feed)
        observations, rewards, labels = [], [], [] # Reset history.

        if episode_number % 25 == 0:
            print('ep: {}, reward: {}, mean reward: {:3f}'.format(
                episode_number, reward_sum, running_reward))

        episode_number += 1
        observation = env.reset()
        reward_sum = 0
