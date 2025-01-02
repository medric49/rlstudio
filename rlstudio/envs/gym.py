import abc

import numpy as np
import gymnasium as gym
from PIL import Image

from rlstudio.envs.common import Environment, TimeStep, StepType
from rlstudio.envs.wrappers import MaxEpisodeLengthWrapper


class GymEnvironment(Environment, abc.ABC):
    def __init__(self, env: gym.Env):
        super().__init__()
        self._env = env
        self._episode_length = None

    def reset(self) -> TimeStep:
        self._episode_length = 0
        observation, _ = self._env.reset()
        reward = np.array(0, dtype=np.float32)
        return TimeStep(step_type=StepType.FIRST, truncated=False, observation=observation, action=None, reward=reward)

    def step(self, action: np.ndarray) -> TimeStep:
        self._episode_length += 1
        f_action = self.transform_action(action)
        observation, reward, terminated, truncated, _ = self._env.step(f_action)
        step_type = StepType.MID if not (terminated or truncated) else StepType.LAST
        reward = np.array(reward, dtype=np.float32)
        return TimeStep(step_type=step_type, truncated=truncated, observation=observation, action=action, reward=reward)

    @property
    def observation_space(self) -> gym.spaces.Box:
        return self._env.observation_space

    def render(self, im_w: int, im_h: int) -> Image:
        return Image.fromarray(self._env.render()).resize((im_w, im_h))

    @abc.abstractmethod
    def transform_action(self, action):
        pass

    @property
    def episode_length(self) -> int:
        return self._episode_length


class DiscreteGymEnvironment(GymEnvironment):
    def __init__(self, env: gym.Env):
        super().__init__(env)

    def transform_action(self, action):
        return action + self._env.action_space.start

    @property
    def action_space(self) -> gym.spaces.Discrete:
        return gym.spaces.Discrete(n=self._env.action_space.n, start=0)


class ContinuousGymEnvironment(GymEnvironment):
    def __init__(self, env: gym.Env):
        super().__init__(env)

    def transform_action(self, action):
        return self._env.action_space.low + (action - self.action_space.low) * (
            (self._env.action_space.high - self._env.action_space.low)
            / (self.action_space.high - self.action_space.low)
        )

    @property
    def action_space(self) -> gym.spaces.Box:
        return gym.spaces.Box(
            low=-np.ones(self._env.action_space.shape, dtype=np.float32),
            high=np.ones(self._env.action_space.shape, dtype=np.float32),
            shape=self._env.action_space.shape,
            dtype=np.float32,
        )


def make_env(task: str = "LunarLander-v3", max_episode_length: int = None) -> GymEnvironment:
    env = gym.make(task, render_mode="rgb_array")

    if not isinstance(env.observation_space, gym.spaces.Box):
        raise TypeError(f"[{env.observation_space.__class__.__name__}] observation space not supported]")

    if isinstance(env.action_space, gym.spaces.Discrete):
        env = DiscreteGymEnvironment(env)
    elif isinstance(env.action_space, gym.spaces.Box):
        env = ContinuousGymEnvironment(env)
    else:
        raise TypeError(f"[{env.action_space.__class__.__name__}] action space not supported")

    if max_episode_length is not None:
        env = MaxEpisodeLengthWrapper(env, max_episode_length)

    return env