import pandas as pd

from abc import ABC, abstractmethod
from typing import Dict, List

from src.epinet.models import EpistemicNetwork, DynamicEpistemicNetwork


class BaseSimulation(ABC):
    def __init__(self, network: EpistemicNetwork, steps: int):
        self.network = network
        self.steps = steps
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
        pass

    def save_results(self):
        # TODO: implement what data should be collected
        # TODO: save the results (what format? -> df?)
        pass


class Simulation(BaseSimulation):

    def __init__(self):
        super().__init__()

    def step(self):
        # TODO: documentation
        self.network.run_evidence_collection()
        self.network.run_credence_update()

    def run(self):
        # TODO: documentation
        i = 0
        while i < self.steps and not self.network.is_consensus():
            self.step()
            # TODO: results geathering
            # self.results append self.examine_network()
            i += 1
        return self.network.is_true_consensus()


class CogsnetSimulation(BaseSimulation):

    def __init__(self, structures: Dict[int, Dict[str, List[str]]]):
        super().__init__()
        self.structures = structures

    def step(self, network):
        network.run_evidence_collection()
        network.run_credence_update()

    def run(self):
        # TODO: move to newtwork init before sim start -> self.network = DynamicEpistemicNetwork(self.structures[min(self.structures.keys())])
        # TODO: change to logging
        print(f'Initial mean credence: {self.network.get_mean_credence()}')
        print(f'Initial action voters distribution: {self.network.get_actions_voters_nr()}')
        for s in sorted(self.structures.keys()):
            i = 0
            while i < self.steps and not self.network.is_consensus():
                self.step(self.network)
                i += 1
            if self.network.is_true_consensus():
                return True
            else:
                self.network.update_structure(self.structures[s])
        return False
