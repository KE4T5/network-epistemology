import matplotlib.pyplot as plt
import networkx as nx

from typing import Tuple

from src.epinet.models import EpistemicNetwork
from src.utils.logger import get_logger


logger = get_logger(__name__)


def plot_network(network: EpistemicNetwork, title: str = None, figsize: Tuple[int, int] = None):
    if not figsize:
        figsize = (10, 5)
    g = network.to_networkx_graph()
    plt.figure(figsize=figsize)

    color_map = []
    for val in [val for (node, val) in g.degree()]:
        if val < 1:
            color_map.append('crimson')
        else:
            color_map.append('royalblue')

    nx.draw_networkx(g, node_color=color_map, with_labels=True)
    if title:
        plt.title(title)
    plt.show()


def plot_sims_results(d, a_numbers):
    # TODO: documentation
    for s in d.keys():
        plt.plot(a_numbers, d[s], label = s)
    plt.xlabel('Nr agents in network')
    plt.ylabel('Probability of correct consensus')
    plt.title('Simulations for different network structures')
    plt.legend()
    plt.show()
