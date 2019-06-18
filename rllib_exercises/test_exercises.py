from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def test_chain_env_spaces(chain_env_cls):
    test_env = chain_env_cls(dict(n=6))
    print("Testing if spaces have been setup correctly...")
    assert test_env.action_space is not None, "Action Space not implemented!"
    assert test_env.observation_space is not None, "Observation Space not implemented!"
    assert not test_env.action_space.contains(2), "Action Space is only [0, 1]"
    assert test_env.action_space.contains(
        1), "Action Space does not contain 1."
    assert not test_env.observation_space.contains(
        6), "Observation Space is only [0..5]"
    assert test_env.observation_space.contains(
        5), "Observation Space is only [0..5]"
    print("Success! You've setup the spaces correctly.")


def test_chain_env_reward(chain_env_cls):
    test_env = chain_env_cls(dict(n=6))
    print("Testing if reward has been setup correctly...")
    test_env.reset()
    assert test_env.step(1)[1] == test_env.small_reward
    assert test_env.state == 0
    assert test_env.step(0)[1] == 0
    assert test_env.state == 1
    test_env.reset()
    total_reward = 0
    for i in range(test_env.n - 1):
        total_reward += test_env.step(0)[1]
    assert total_reward == 0, "Expected {} reward; got {}".format(
        0, total_reward)
    for i in range(3):
        assert test_env.step(0)[1] == test_env.large_reward
    assert test_env.step(1)[1] == test_env.small_reward
    print("Success! You've setup the rewards correctly.")


def test_chain_env_behavior(chain_env_cls):
    test_env = chain_env_cls(dict(n=6))
    print("Testing if behavior has been changed...")
    test_env.reset()
    assert test_env.state == 0
    test_env.step(1)
    assert test_env.state == 0
    test_env.step(0)
    assert test_env.state == 1
    test_env.reset()
    assert test_env.state == 0
    for i in range(1, test_env.n):
        test_env.step(0)
        assert test_env.state == i
    test_env.step(0)
    assert test_env.state == test_env.n - 1
    test_env.step(1)
    assert test_env.state == 0
    print("Success! Behavior of environment is correct.")
