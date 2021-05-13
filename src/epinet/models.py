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
        g = nx.Graph(structure)
        g.remove_edges_from(nx.selfloop_edges(g))
        undirected_structure = nx.convert.to_dict_of_lists(g)
        self.adjacency_list = undirected_structure
        self.id_to_agents = {int(i): Agent(int(i), random.uniform(0, 1), undirected_structure[i]) for i in
                             undirected_structure.keys()}
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

    def is_consensus(self, subset_ids: Set[str] = None) -> bool:
        """
        Checks if there is a consensus regarding superiority of one of the actions.
        """
        if not subset_ids:
            subset_ids = self.get_connected_agents_ids()
        return self.is_alpha_consensus(subset_ids) or self.is_beta_consensus(subset_ids)

    def get_connected_agents_ids(self) -> Set[str]:
        connected_agents_ids = {i for i, a in self.id_to_agents.items() if a.neighbors}
        return connected_agents_ids

    def get_state(self, subset_ids: Set[str] = None) -> str:
        if not subset_ids:
            subset_ids = self.get_connected_agents_ids()
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
        if not subset_ids:
            subset_ids = self.get_connected_agents_ids()
        agents = self.get_agents(subset_ids)
        return np.mean([agent.credence for agent in agents])

    def get_actions_voters_nr(self, subset_ids: Set[str] = None) -> Tuple[int, int]:
        if not subset_ids:
            subset_ids = self.get_connected_agents_ids()
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

    def get_status(self):
        result = []
        state = self.get_state()
        alpha_voters, beta_voters = self.get_actions_voters_nr()
        mean_credence = self.get_mean_credence()
        connected_comps = self.get_connected_components()
        connected_comps_nr = len(connected_comps)
        for connected_component_id, subset in enumerate(connected_comps):
            cc_size = len(subset)
            cc_state = self.get_state(subset)
            cc_alpha_voters, cc_beta_voters = self.get_actions_voters_nr(subset)
            cc_mean_credence = self.get_mean_credence(subset)
            row = (state, alpha_voters, beta_voters, mean_credence, connected_comps_nr, connected_component_id, cc_size, cc_state, cc_alpha_voters, cc_beta_voters, cc_mean_credence)
            result.append(row)
        return result

    def get_current_status(self):
        connected_comps = self.get_connected_components()
        biggest_cc = max(connected_comps, key=len)
        alpha_voters, beta_voters = self.get_actions_voters_nr()
        biggest_cc_av, biggest_cc_bv = self.get_actions_voters_nr(biggest_cc)
        status = {
            'full_net_state': self.get_state(),
            'full_net_av': alpha_voters,
            'full_net_bv': beta_voters,
            'full_net_cred': self.get_mean_credence(),
            'big_cc_state': self.get_state(biggest_cc),
            'big_cc_av': biggest_cc_av,
            'big_cc_bv': biggest_cc_bv,
            'big_cc_cred': self.get_mean_credence(biggest_cc),
            #'rest_cc_status': 1,
            #'rest_cc_av': 1,
            #'rest_cc_bv': 1,
            #'rest_cc_cred': 1
        }
        return status


class StaticEpistemicNetwork(EpistemicNetwork):
    pass


class DynamicEpistemicNetwork(EpistemicNetwork):

    def update_structure(self, adjacency_list: Dict[str, Set[str]]):
        """

        :param adjacency_list:
        :return:
        """
        g = nx.Graph(adjacency_list)
        g.remove_edges_from(nx.selfloop_edges(g))
        adjacency_list = nx.convert.to_dict_of_lists(g)
        self.adjacency_list = adjacency_list
        #print(self.adjacency_list)

        current_agents_ids = set(self.id_to_agents.keys())
        new_structure_agent_ids = set(self.adjacency_list.keys())

        ids_agents_to_detach = current_agents_ids.difference(new_structure_agent_ids)
        ids_agents_to_update = current_agents_ids.intersection(new_structure_agent_ids)
        ids_agents_to_create = new_structure_agent_ids.difference(current_agents_ids)

        #logger.info(f'Agents to detach: {ids_agents_to_detach}')
        #logger.info(f'Agents to update: {ids_agents_to_update}')
        #logger.info(f'Agents to create: {ids_agents_to_create}')

        # 1.  agents not present in new structure
        for agent_id in ids_agents_to_detach:
            self.id_to_agents[agent_id].set_neighbors(set())
            self.adjacency_list[agent_id] = set()

        # 2. Update agents present in new structure
        for agent_id in ids_agents_to_update:
            self.id_to_agents[agent_id].set_neighbors(self.adjacency_list[agent_id])

        # 3. Create new agents for ids present only in new structure
        for agent_id in ids_agents_to_create:
            self.id_to_agents[agent_id] = Agent(agent_id, random.uniform(0, 1), self.adjacency_list[agent_id])

    def get_state_of_connected_components(self):
        pass
