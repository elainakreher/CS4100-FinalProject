# Agents

This folder contains the AI agents used in the Minesweeper project. Each agent represents a different approach to solving Minesweeper and will be evaluated based on metrics such as win rate, runtime, and decision quality.

## BaseAgent

The BaseAgent provides a common interface for all agents. It contains shared functionality for interacting with the Minesweeper API, managing games, and retrieving board states. All other agents inherit from this class.

## RandomAgent

Uses no intelligence or strategy. The agent identifies all unrevealed cells and randomly selects one to reveal. This serves as a baseline for comparing the performance of more advanced AI approaches.

## RuleBasedAgent

Uses deterministic Minesweeper logic to identify guaranteed safe cells and mine locations. The agent applies standard deduction rules based on neighboring clue numbers and only makes moves that can be logically justified.

## ProbabilityAgent

Combines logical reasoning with probabilistic decision-making. When no guaranteed safe move exists, the agent estimates the likelihood that each unrevealed cell contains a mine and selects the cell with the lowest estimated risk.

## RLAgent

Uses reinforcement learning to learn a strategy through repeated gameplay. The agent receives rewards for safe moves and successful games, and penalties for mistakes, gradually improving its decision-making policy based on experience rather than predefined rules.