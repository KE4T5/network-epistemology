import pandas as pd

from abc import ABC, abstractmethod
from typing import Dict, Set

from src.epinet.models import EpistemicNetwork, DynamicEpistemicNetwork
from src.utils.logger import get_logger


logger = get_logger(__name__)


class BaseSimulation(ABC):
    def __init__(self, network: EpistemicNetwork, nr_iterations: int):
        self.network = network
        self.nr_iterations = nr_iterations
        self.results = pd.DataFrame()

    #@abstractmethod
    #def step(self):
    #    # TODO: documentation
    #    self.network.run_evidence_collection()
    #    self.network.run_credence_update()

    @abstractmethod
    def play_iteration(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def examine_network(self):
        # TODO: implement network states geathering
        pass

    def save_results(self):
        # TODO: implement what data should be collected
        # TODO: save the results (what format? -> df?)
        pass


class Simulation(BaseSimulation):

    def __init__(self, network: EpistemicNetwork, nr_iterations: int):
        super().__init__(network, nr_iterations)

    def get_network_details(self):
        pass

    def play_iteration(self):
        # TODO: documentation
        self.network.run_evidence_collection()
        self.network.run_credence_update()

    def run(self, verbose: bool = False):
        # TODO: documentation
        i = 0
        while i < self.nr_iterations and not self.network.is_consensus():
            self.play_iteration()
            if verbose:
                self.network.describe()
            # TODO: results geathering
            # self.results append self.examine_network()
            i += 1
        return self.network.get_state(), i


class CogsnetSimulation(BaseSimulation):

    def __init__(self, network: DynamicEpistemicNetwork, nr_iterations: int, cogsnets: Dict[int, Dict[str, Set[str]]]):
        super().__init__(network, nr_iterations)
        self.cogsnets = cogsnets

    def play_iteration(self):
        self.network.run_evidence_collection()
        self.network.run_credence_update()

    def run(self, verbose: bool = False):
        # Should return simulation results -> step by step (day by day)
        # TODO: move to newtwork init before sim start -> self.network = DynamicEpistemicNetwork(self.structures[min(self.structures.keys())])
        # TODO: change to logging
        #print(f'Initial mean credence: {self.network.get_mean_credence()}')
        #print(f'Initial action voters distribution: {self.network.get_actions_voters_nr()}')

        time_step_results = {}
        consensus_time = None

        min_ts = int(min(self.cogsnets.keys()))
        max_ts = max(self.cogsnets.keys())

        for s in sorted(self.cogsnets.keys()):
            i = 0
            while i < self.nr_iterations:  # and not self.network.is_consensus(): TODO: reconcider it
                self.play_iteration()
                i += 1

            # Remove early simulation stopping: TODO: reconcider it
            if self.network.is_consensus():
                consensus_time = int(s) - min_ts
            #    if verbose:
            #        self.network.describe()
            #        logger.info(f'Consensus obtained in iteration nr {i}.')
            #    print(self.network.get_status())
            #    return self.network.get_state(), s
            #else:
            time_step_results[s] = self.network.get_current_status()
            self.network.update_structure(self.cogsnets[s])

        return time_step_results, time_step_results[max_ts], consensus_time
