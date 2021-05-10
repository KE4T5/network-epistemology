from numpy import random
from typing import Set

from src.utils.logger import get_logger


logger = get_logger(__name__)


class Agent:

    def __init__(self, agent_id: str, credence: float, neighbors: Set[str]):
        self.id = agent_id
        self.credence = credence
        self.neighbors = neighbors
        self.trials_nr = 0
        self.successes_nr = 0
        logger.info(f'Agent {agent_id} created successfully!')

    def get_evidence(self, trials_nr: int, alpha_action_payoff: float, beta_action_payoff: float):
        # TODO: documentation
        self.trials_nr, self.successes_nr = 0, 0
        if self.credence > alpha_action_payoff:
            self.trials_nr = trials_nr
            self.successes_nr = random.binomial(trials_nr, beta_action_payoff)

    def update_credence(self, n: int, k: int, epsilon: float):
        # TODO: documentation
        # TODO: check if magic number 0.5 should not be replaced with alpha_action_payoff
        self.credence = 1 / (1 + (1 - self.credence) * (
                    ((0.5 - epsilon) / (0.5 + epsilon)) ** (
                        2 * k - n)) / self.credence)

    def set_neighbors(self, neighbors: Set[str]):
        self.neighbors = neighbors
