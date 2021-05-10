import networkx as nx
import numpy as np

from abc import ABC, abstractmethod
from networkx.algorithms.components import connected_components
from numpy import random
from typing import Dict, List, Set, Tuple

from src.epinet.agent import Agent
from src.utils.logger import get_logger


logger = get_logger(__name__)


class EpistemicNetwork(ABC):
    # TODO: documentation
    STATE_CORRECT_CONSENSUS = 'Correct Consensus'
    STATE_INCORRECT_CONSENSUS = 'Incorrect Consensus'
    STATE_CORRECT_DISAGREEMENT = 'Correct Disagreement'
    STATE_INCORRECT_DISAGREEMENT = 'Incorrect Disagreement'

    def __init__(
            self,
            structure: Dict[str, Set[str]],
            alpha_action_payoff: float,
            beta_action_payoff: float,
            consensus_threshold: float,
            trials_nr: int
    ):
        self.adjacency_list = structure
        self.id_to_agents = {i: Agent(i, random.uniform(0, 1), structure[i]) for i in
                             structure.keys()}
        self.alpha_action_payoff = alpha_action_payoff
        self.beta_action_payoff = beta_action_payoff
        self.epsilon = self.beta_action_payoff - self.alpha_action_payoff
        self.consensus_threshold = consensus_threshold
        self.nr_trials = trials_nr

    def run_evidence_collection(self):
        for agent in self.id_to_agents.values():
            agent.get_evidence(self.nr_trials, self.alpha_action_payoff, self.beta_action_payoff)

    def run_credence_update(self):
        for agent in self.id_to_agents.values():
            sum_trials_nr = agent.trials_nr + sum(
                [self.id_to_agents[neighbor].trials_nr for neighbor in agent.neighbors if neighbor in self.id_to_agents.keys()])
            sum_successes_nr = agent.successes_nr + sum(
                [self.id_to_agents[neighbor].successes_nr for neighbor in agent.neighbors if neighbor in self.id_to_agents.keys()])
            if sum_trials_nr > 0:
                agent.update_credence(sum_trials_nr, sum_successes_nr, self.epsilon)

    def get_agents(self, subset_ids: Set[str]) -> List[Agent]:
        if subset_ids:
            agents = [agent for agent_id, agent in self.id_to_agents.items() if agent_id in subset_ids]
        else:
            agents = self.id_to_agents.values()
        return agents

    def is_incorrect_disagreement(self, subset_ids: Set[str] = None) -> bool:
        is_correct_disagreement = False
        alpha_action_voters_nr, beta_action_voters_nr = self.get_actions_voters_nr(subset_ids)
        if not self.is_alpha_consensus() and alpha_action_voters_nr >= beta_action_voters_nr:
            is_correct_disagreement = True
        return is_correct_disagreement

    def is_correct_disagreement(self, subset_ids: Set[str] = None) -> bool:
        is_incorrect_disagreement = False
        alpha_action_voters_nr, beta_action_voters_nr = self.get_actions_voters_nr(subset_ids)
        if not self.is_beta_consensus() and beta_action_voters_nr > alpha_action_voters_nr:
            is_incorrect_disagreement = True
        return is_incorrect_disagreement

    def is_alpha_consensus(self, subset_ids: Set[str] = None) -> bool:
        agents = self.get_agents(subset_ids)
        is_alpha_consensus = all( agent.credence < self.alpha_action_payoff for agent in agents)
        return is_alpha_consensus

    def is_beta_consensus(self, subset_ids: Set[str] = None) -> bool:
        agents = self.get_agents(subset_ids)
        is_beta_consensus = all(agent.credence > self.consensus_threshold for agent in agents)
        return is_beta_consensus

    def is_consensus(self) -> bool:
        """
        Checks if there is a consensus regarding superiority of one of the actions.
        """
        return self.is_alpha_consensus() or self.is_beta_consensus()

    def get_state(self, subset_ids: Set[str] = None) -> str:
        state = ''
        if self.is_alpha_consensus(subset_ids):
            state = self.STATE_INCORRECT_CONSENSUS
        elif self.is_beta_consensus(subset_ids):
            state = self.STATE_CORRECT_CONSENSUS
        elif self.is_incorrect_disagreement(subset_ids):
            state = self.STATE_INCORRECT_DISAGREEMENT
        elif self.is_correct_disagreement(subset_ids):
            state = self.STATE_CORRECT_DISAGREEMENT
        return state

    def get_mean_credence(self, subset_ids: Set[str] = None) -> float:
        agents = self.get_agents(subset_ids)
        return np.mean([agent.credence for agent in agents])

    def get_actions_voters_nr(self, subset_ids: Set[str] = None) -> Tuple[int, int]:
        agents = self.get_agents(subset_ids)
        alpha_action_voters_nr = len(list(a for a in agents if a.credence <= self.alpha_action_payoff))
        beta_action_voters_nr = len(list(a for a in agents if a.credence > self.alpha_action_payoff))
        return alpha_action_voters_nr, beta_action_voters_nr

    def to_networkx_graph(self):
        return nx.Graph(self.adjacency_list)

    def get_connected_components(self) -> List[Set[str]]:
        g = self.to_networkx_graph()
        cc = [cc for cc in connected_components(g)]
        return cc

    def get_states_of_connected_components(self) -> List[Tuple[int, str]]:
        cc = self.get_connected_components()
        states = []
        for i, c in enumerate(cc):
            state = self.get_state(c)
            states.append((len(c), state))
        return states

    def print_agents(self):
        for agent in self.id_to_agents.values():
            print(f" -> Agent {agent.id}, cred: {agent.credence:.2f}, trials_nr: {agent.trials_nr}, succ_nr: {agent.successes_nr}, neighbours: {agent.neighbors}")

    def describe(self):
        print('Agents details')
        self.print_agents()
        print(f'Consensus check: {self.is_consensus()}')
        print(f'State: {self.get_state()}')
        print(f'Mean credence: {self.get_mean_credence()}')
        print(f'Action voters: {self.get_actions_voters_nr()}')
        print()


class StaticEpistemicNetwork(EpistemicNetwork):
    pass


class DynamicEpistemicNetwork(EpistemicNetwork):

    def update_structure(self, adjacency_list: Dict[str, Set[str]]):
        """

        :param adjacency_list:
        :return:
        """
        self.adjacency_list = adjacency_list

        current_agents_ids = set(self.id_to_agents.keys())
        new_structure_agent_ids = set(adjacency_list.keys())

        ids_agents_to_detach = current_agents_ids.difference(new_structure_agent_ids)
        ids_agents_to_update = current_agents_ids.intersection(new_structure_agent_ids)
        ids_agents_to_create = new_structure_agent_ids.difference(current_agents_ids)

        logger.info(f'Agents to detach: {ids_agents_to_detach}')
        logger.info(f'Agents to update: {ids_agents_to_update}')
        logger.info(f'Agents to create: {ids_agents_to_create}')

        # 1.  agents not present in new structure
        for agent_id in ids_agents_to_detach:
            self.id_to_agents[agent_id].set_neighbors(set())
            self.adjacency_list[agent_id] = set()

        # 2. Update agents present in new structure
        for agent_id in ids_agents_to_update:
            self.id_to_agents[agent_id].set_neighbors(adjacency_list[agent_id])

        # 3. Create new agents for ids present only in new structure
        for agent_id in ids_agents_to_create:
            self.id_to_agents[agent_id] = Agent(agent_id, random.uniform(0, 1), adjacency_list[agent_id])

    def get_state_of_connected_components(self):
        pass
