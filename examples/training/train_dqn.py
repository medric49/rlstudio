from dataclasses import asdict

import gymnasium as gym

from envquest import arguments as args, envs, agents, trainers


def main():
    # Training arguments
    arguments = args.TrainingArguments(
        agent=args.DQNAgentArguments(), logging=args.LoggingArguments(save_agent_snapshots=False)
    )

    # Define environment
    env = envs.gym.make_env(**asdict(arguments.env))

    # Define agent
    if isinstance(env.action_space, gym.spaces.Discrete):
        agent = agents.dqn.DiscreteQNetAgent(
            mem_capacity=arguments.agent.mem_capacity,
            discount=arguments.agent.discount,
            n_steps=arguments.agent.n_steps,
            lr=arguments.agent.lr,
            tau=arguments.agent.tau,
            eps_start=arguments.agent.eps_start,
            eps_end=arguments.agent.eps_end,
            eps_step_duration=arguments.agent.eps_step_duration,
            eps_decay=arguments.agent.eps_decay,
            observation_space=env.observation_space,
            action_space=env.action_space,
        )
    else:
        raise ValueError(
            f"'[{arguments.env.task}]' task is not a discrete gym environment. This script currently only supports discrete environments."
        )

    # Define trainer
    trainer = trainers.Trainer(env, agent, arguments)

    # Start training
    trainer.train()


if __name__ == "__main__":
    main()
