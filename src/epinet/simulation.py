import pandas as pd

from abc import ABC, abstractmethod
from typing import Dict, Set

from src.epinet.models import EpistemicNetwork, DynamicEpistemicNetwork
from src.utils.logger import get_logger


logger = get_logger(__name__)


class BaseSimulation(ABC):
    def __init__(self, network: EpistemicNetwork, nr_steps: int):
        self.network = network
        self.steps = nr_steps
        self.results = pd.DataFrame()

    #@abstractmethod
    #def step(self):
    #    # TODO: documentation
    #    self.network.run_evidence_collection()
    #    self.network.run_credence_update()

    @abstractmethod
    def step(self):
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

    def __init__(self, network: EpistemicNetwork, steps_nr: int):
        super().__init__(network, steps_nr)

    def get_network_details(self):
        pass

    def step(self):
        # TODO: documentation
        self.network.run_evidence_collection()
        self.network.run_credence_update()

    def run(self, verbose: bool = False):
        # TODO: documentation
        i = 0
        while i < self.steps and not self.network.is_consensus():
            self.step()
            if verbose:
                self.network.describe()
            # TODO: results geathering
            # self.results append self.examine_network()
            i += 1
        return self.network.get_state(), i


class CogsnetSimulation(BaseSimulation):

    def __init__(self, network: EpistemicNetwork, nr_steps: int, cogsnets: Dict[int, Dict[str, Set[str]]]):
        super().__init__(network, nr_steps)
        self.cogsnets = cogsnets

    def step(self, network):
        network.run_evidence_collection()
        network.run_credence_update()

    def run(self, verbose: bool = False):
        # TODO: move to newtwork init before sim start -> self.network = DynamicEpistemicNetwork(self.structures[min(self.structures.keys())])
        # TODO: change to logging
        print(f'Initial mean credence: {self.network.get_mean_credence()}')
        print(f'Initial action voters distribution: {self.network.get_actions_voters_nr()}')
        if verbose:
            self.network.describe()
        for s in sorted(self.cogsnets.keys()):
            if verbose:
                logger.info(f'Time step nr {s} started.')
            i = 0
            while i < self.steps and not self.network.is_consensus():
                if verbose:
                    logger.info(f'Iteration nr {i} started.')
                self.step(self.network)
                i += 1
            if self.network.is_consensus():
                if verbose:
                    self.network.describe()
                    logger.info(f'Consensus obtained in iteration nr {i}.')
                return self.network.get_state(), s
            else:
                self.network.update_structure(self.cogsnets[s])
        if verbose:
            self.network.describe()
            logger.info('Consensus was not obtained.')
        return self.network.get_state(), -1
