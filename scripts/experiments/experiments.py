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

# Time Step Metrics:

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
                    sim_set_results = {
                        'state': [],
                        'av': [],
                        'bv': [],
                        'cred': [],
                        'cc_state': [],
                        'cc_av': [],
                        'cc_bv': [],
                        'cc_cred': [],
                        'cons_time': []
                    }
                    for s_nr in range(nr_simulations):
                        network = DynamicEpistemicNetwork(base_structure, alpha_payoff, beta_payoff, consensus_threshold, nr_trials)
                        simulation = CogsnetSimulation(network, nr_iterations_per_step, next_structures)
                        time_step_results, final_res, cons_time = simulation.run()

                        sim_set_results['state'].append(final_res['full_net_state'])
                        sim_set_results['av'].append(final_res['full_net_av'])
                        sim_set_results['bv'].append(final_res['full_net_bv'])
                        sim_set_results['cred'].append(final_res['full_net_cred'])
                        sim_set_results['cc_state'].append(final_res['big_cc_state'])
                        sim_set_results['cc_av'].append(final_res['big_cc_av'])
                        sim_set_results['cc_bv'].append(final_res['big_cc_bv'])
                        sim_set_results['cc_cred'].append(final_res['big_cc_cred'])
                        sim_set_results['cons_time'].append(cons_time)
                    # calc res row based on the aggregated sim results


consensus_threshold = 0.999  # consensus_threshold_values = []
nr_simulations = 100
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

# Time Step Metrics:

def run_experiment_2(cogsnets, beta_payoff_values, nr_trials_values, nr_iterations_per_step_values):
    struct_min_key = int(min(cogsnets.keys()))
    base_structure = cogsnets[struct_min_key]
    next_structures = {i: c for i, c in cogsnets.items() if i != struct_min_key}

    results = []

    for beta_payoff in beta_payoff_values:
        # for consensus_threshold in consensus_threshold_values:
        for nr_trials in nr_trials_values:
            for nr_iterations_per_step in nr_iterations_per_step_values:
                # print(f"Performing simulation for config: {beta_payoff}, {consensus_threshold}, {nr_trials}, {nr_iterations_per_step}")
                sim_set_results = {
                    'state': [],
                    'av': [],
                    'bv': [],
                    'cred': [],
                    'cc_state': [],
                    'cc_av': [],
                    'cc_bv': [],
                    'cc_cred': [],
                    'cons_time': []
                }
                for s_nr in tqdm(range(nr_simulations)):
                    network = DynamicEpistemicNetwork(base_structure, alpha_payoff, beta_payoff, consensus_threshold,
                                                      nr_trials)
                    simulation = CogsnetSimulation(network, nr_iterations_per_step, next_structures)
                    time_step_results, final_res, cons_time = simulation.run()

                    av_prec = 100 * final_res['full_net_av'] / (final_res['full_net_av'] + final_res['full_net_bv'])
                    bv_prec = 100 * final_res['full_net_bv'] / (final_res['full_net_av'] + final_res['full_net_bv'])

                    cc_av_prec = 100 * final_res['big_cc_av'] / (final_res['big_cc_av'] + final_res['big_cc_bv'])
                    cc_bv_prec = 100 * final_res['big_cc_bv'] / (final_res['big_cc_av'] + final_res['big_cc_bv'])

                    sim_set_results['state'].append(final_res['full_net_state'])
                    sim_set_results['av'].append(final_res['full_net_av'])
                    sim_set_results['bv'].append(final_res['full_net_bv'])
                    sim_set_results['cred'].append(final_res['full_net_cred'])
                    sim_set_results['cc_state'].append(final_res['big_cc_state'])
                    sim_set_results['cc_av'].append(final_res['big_cc_av'])
                    sim_set_results['cc_bv'].append(final_res['big_cc_bv'])
                    sim_set_results['cc_cred'].append(final_res['big_cc_cred'])
                    sim_set_results['cons_time'].append(cons_time)

                    res = {
                        'beta_payoff': beta_payoff,
                        'nr_trials': nr_trials,
                        'nr_iterations_per_step': nr_iterations_per_step,
                        'state': final_res['full_net_state'],
                        'av': av_prec,
                        'bv': bv_prec,
                        'cred': final_res['full_net_cred'],
                        'cc_state': final_res['big_cc_state'],
                        'cc_av': cc_av_prec,
                        'cc_bv': cc_bv_prec,
                        'cc_cred': final_res['big_cc_cred'],
                        'cons_time': cons_time
                    }

                    results.append(res)
    df = pd.DataFrame(results)
    return results

cogsnets = {k: step_to_adjacency_list_2[k] for k in range(10, 110)}
beta_payoff_values = [0.5005, 0.501, 0.505, 0.51, 0.55, 0.6]  # [0.501, 0.51, 0.55, 0.6, 0.7, 0.8]
nr_trials_values = [1, 5, 10, 50, 100] # [1, 5, 10, 50, 100, 1000]
nr_iterations_per_step_values = [5]  # [1, 3, 5, 10, 50, 100]

r1 = run_experiment_1(cogsnets, beta_payoff_values, nr_trials_values , nr_iterations_per_step_values)