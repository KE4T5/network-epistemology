from src.epinet.models import DynamicEpistemicNetwork
from src.epinet.simulation import CogsnetSimulation
from src.utils.logger import get_logger


logger = get_logger(__name__)

# Network structure
cogsnets = {}
beta_payoff_values = [0.501, 0.51, 0.55, 0.6, 0.7, 0.8]
nr_trials_values = [1, 5, 10, 50, 100, 1000]
nr_iterations_per_step_values = [1, 3, 5, 10, 50, 100]
consensus_threshold = 0.999  # consensus_threshold_values = []
nr_simulations = 2
alpha_payoff = 0.5


# Results Data Frame format
# cogsnets | consensus_threshold | alpha_payoff | beta_payoff | nr_trials | nr_iterations_per_step || step |
#   CORRECT_CONSENSUS | INCORRECT_CONSENSUS | CORRECT_DISAGREEMENT | INCORRECT_DISAGREEMENT | ALPHA_VOTERS |
#   BETA_VOTERS | MEAN_CREDENCE |
#   BCC_CORRECT_CONSENSUS | BCC_INCORRECT_CONSENSUS | BCC_CORRECT_DISAGREEMENT |
#   BCC_INCORRECT_DISAGREEMENT | BCC_ALPHA_VOTERS | BCC_BETA_VOTERS | BCC_MEAN_CREDENCE |
#   REST_CC_CORRECT_CONSENSUS | REST_CC_INCORRECT_CONSENSUS | REST_CC_CORRECT_DISAGREEMENT |
#   REST_CC_INCORRECT_DISAGREEMENT | REST_CC_ALPHA_VOTERS | REST_CC_BETA_VOTERS | REST_CC_MEAN_CREDENCE |
#

def run_experiment_1(cogsnets, beta_payoff_values, consensus_threshold_values, nr_trials_values, nr_iterations_per_step_values):
    struct_min_key = 1  # TODO: implement selecting the smallest one
    base_structure = cogsnets[struct_min_key]
    next_structures = {i: c for i, c in cogsnets.items() if i != struct_min_key}

    results = []

    for beta_payoff in beta_payoff_values:
        #for consensus_threshold in consensus_threshold_values:
            for nr_trials in nr_trials_values:
                for nr_iterations_per_step in nr_iterations_per_step_values:
                    logger.info(f"Performing simulation for config: {beta_payoff}, {consensus_threshold}, {nr_trials}, {nr_iterations_per_step}")
                    simulations_res = []
                    for s_nr in nr_simulations:
                        network = DynamicEpistemicNetwork(base_structure, alpha_payoff, beta_payoff, consensus_threshold, nr_trials)
                        simulation = CogsnetSimulation(network, nr_iterations_per_step, next_structures)
                        sim_res = simulation.run()
                        simulations_res.append(sim_res)

                    # calc res row based on the aggregated sim results
                    for s in len(cogsnets.keys()):
