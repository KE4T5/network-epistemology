import numpy as np

from abc import ABC, abstractmethod
from numpy import random
from typing import Dict, List, Tuple

from src.epinet.agent import Agent


class EpistemicNetwork(ABC):
    # TODO: documentation
    STATE_ALPHA_CONSENSUS = 'Alpha consensus'
    STATE_BETA_CONSENSUS = 'Beta consensus'
    STATE_UNDECIDED = 'Undecided'

    def __init__(
            self,
            structure: Dict[str, List[str]],
            alpha_action_payoff: float,
            beta_action_payoff: float,
            consensus_threshold: float,
            nr_trials: int
    ):
        self.structure = structure
        self.agents = {i: Agent(i, random.uniform(0, 1), structure[i]) for i in
                       structure.keys()}
        self.alpha_action_payoff = alpha_action_payoff
        self.beta_action_payoff = beta_action_payoff
        self.epsilon = self.beta_action_payoff - self.alpha_action_payoff
        self.consensus_threshold = consensus_threshold
        self.nr_trials = nr_trials

    def run_evidence_collection(self):
        for agent in self.agents.values():
            agent.get_evidence(self.nr_trials, self.alpha_action_payoff, self.beta_action_payoff)

    def run_credence_update(self):
        for agent in self.agents.values():
            n = agent.n + sum(
                [self.agents[neighbor].n for neighbor in agent.neighbors if neighbor in self.agents.keys()])
            k = agent.k + sum(
                [self.agents[neighbor].k for neighbor in agent.neighbors if neighbor in self.agents.keys()])
            if n > 0:
                agent.update_credence(n, k, self.epsilon)

    def is_alpha_consensus(self):
        is_alpha_consensus = all(
            agent.credence < self.alpha_action_payoff for agent in
            self.agents.values())
        return is_alpha_consensus

    def is_beta_consensus(self):
        is_beta_consensus = all(
            agent.credence > self.consensus_threshold for agent in
            self.agents.values())
        return is_beta_consensus

    def is_consensus(self):
        """
        Checks if there is a consensus regarding superiority of one of the actions.
        """
        return self.is_alpha_consensus() or self.is_beta_consensus()

    def get_state(self):
        state = self.STATE_UNDECIDED
        if self.is_alpha_consensus():
            state = self.STATE_ALPHA_CONSENSUS
        elif self.is_beta_consensus():
            state = self.STATE_BETA_CONSENSUS
        return state

    def get_mean_credence(self):
        return np.mean([agent.credence for agent in self.agents.values()])

    def get_actions_voters_nr(self):
        base_action_voters_nr = len(list(a for a in self.agents.values() if a.credence <= self.alpha_action_payoff))
        beta_action_voters_nr = len(list(a for a in self.agents.values() if a.credence > self.alpha_action_payoff))
        actions_voters_nr = {
            self.alpha_action_payoff: base_action_voters_nr,
            self.beta_action_payoff: beta_action_voters_nr
        }
        return actions_voters_nr

    def describe(self):
        for agent in self.agents.values():
            print(f"- Agent {agent.id}, {agent.credence}, {agent.n}, {agent.k}, {agent.neighbors}")
        print()


class StaticEpistemicNetwork(EpistemicNetwork):
    pass


class DynamicEpistemicNetwork(EpistemicNetwork):

    def update_structure(self, structure: Dict[str, List[str]]):
        for a in self.agents.values():
            if a in structure.keys():  # TODO: verify if this is a valid implementation
                a.set_neighbors(structure[a.id])
            else:
                a.set_neighbors([])
        self.structure = structure
