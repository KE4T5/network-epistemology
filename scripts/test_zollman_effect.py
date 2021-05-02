import networkx as nx
import numpy as np

from typing import Dict, List

from src.epinet.models import EpistemicNetwork
from src.epinet.simulation import Simulation
from src.visualizations.visualizations import plot_sims_results


SIM_MAX_STEPS = 10000


def test_complete(nr_nodes: int, nr_sims: int) -> float:
    g = nx.complete_graph(nr_nodes)
    l = nx.convert.to_dict_of_lists(g)
    res = []
    for i in range(nr_sims):
        n = EpistemicNetwork(l)
        s = Simulation(n, SIM_MAX_STEPS)
        p_res = s.run()
        res.append(1 if p_res else 0)
    return np.mean(res)


def test_cycle(nr_nodes: int, nr_sims: int) -> float:
    g = nx.cycle_graph(nr_nodes)
    l = nx.convert.to_dict_of_lists(g)
    res = []
    for i in range(nr_sims):
        n = EpistemicNetwork(l)
        s = Simulation(n, SIM_MAX_STEPS)
        p_res = s.run()
        res.append(1 if p_res else 0)
    return np.mean(res)


def test_wheel(nr_nodes: int, nr_sims: int) -> float:
    g = nx.wheel_graph(nr_nodes)
    l = nx.convert.to_dict_of_lists(g)
    res = []
    for i in range(nr_sims):
        n = EpistemicNetwork(l)
        s = Simulation(n, SIM_MAX_STEPS)
        p_res = s.run()
        res.append(1 if p_res else 0)
    return np.mean(res)


def test_zollman_effect(agent_nrs: List[int] = None, sims_nr: int = 10000) -> Dict[str, List[float]]:
    if not agent_nrs:
        agent_nrs = [5, 6, 7, 8, 9, 10]

    results = {
        'cycle': [],
        'wheel': [],
        'complete': []
    }

    for nr in agent_nrs:
        # Complete
        res = test_complete(nr, sims_nr)
        results['complete'].append(res)

        # Wheel
        res = test_wheel(nr, sims_nr)
        results['wheel'].append(res)

        # Cycle
        res = test_cycle(nr, sims_nr)
        results['cycle'].append(res)

    plot_sims_results(results, agent_nrs)  # TODO: save the plot and move to visualization
    return results


if __name__ == "__main__":
    results = test_zollman_effect()
    # TODO: save plot
