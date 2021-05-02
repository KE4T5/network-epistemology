from numpy import random
from typing import List


class Agent:

    def __init__(self, i: str, credence: float, neighbors: List[str]):
        self.id = i
        self.credence = credence
        self.neighbors = neighbors
        self.n = 0
        self.k = 0

    def get_evidence(self, n_trials: int, alpha_action_payoff: float, beta_action_payoff: float):
        # TODO: documentation
        self.n, self.k = 0, 0
        if self.credence > alpha_action_payoff:
            self.n = n_trials
            self.k = random.binomial(n_trials, beta_action_payoff)

    def update_credence(self, n: int, k: int, epsilon: float):
        # TODO: documentation
        self.credence = 1 / (1 + (1 - self.credence) * (
                    ((0.5 - epsilon) / (0.5 + epsilon)) ** (
                        2 * k - n)) / self.credence)

    def set_neighbors(self, neighbors: List[str]):
        self.neighbors = neighbors
