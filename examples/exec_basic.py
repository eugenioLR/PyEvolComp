from pyevolcomp import ObjectiveFunc, ParentSelection, SurvivorSelection, ParamScheduler
from pyevolcomp.SearchMethods import GeneralSearch, MemeticSearch
from pyevolcomp.Operators import OperatorReal, OperatorInt, OperatorBinary
from pyevolcomp.Initializers import UniformVectorInitializer
from pyevolcomp.Algorithms import *
from pyevolcomp.benchmarks import *

import argparse

def run_algorithm(alg_name, memetic, save_state):
    params = {
        "stop_cond": "time_limit",
        "progress_metric": "time_limit",
        "time_limit": 1.0,
        "cpu_time_limit": 10.0,
        "ngen": 1000,
        "neval": 6e5,
        "fit_target": 1e-10,

        "verbose": True,
        "v_timer": 0.5
    }

    objfunc = Sphere(10, "min")
    pop_initializer = UniformVectorInitializer(10, objfunc.low_lim, objfunc.up_lim)

    mut_params = ParamScheduler("Linear", {"method":"Cauchy", "F": [0.01, 0.00001]})
    parent_params = ParamScheduler("Linear", {"amount": 20})
    # select_params = ParamScheduler("Linear")

    mutation_op = OperatorReal("RandNoise", mut_params)
    cross_op = OperatorReal("Multipoint")
    parent_sel_op = ParentSelection("Best", parent_params)
    selection_op = SurvivorSelection("(m+n)")
    
    mem_select = ParentSelection("Best", {"amount": 5})
    neihbourhood_op = OperatorReal("RandNoise", {"method":"Cauchy", "F": 0.0002})
    local_search =  LocalSearch(neihbourhood_op, {"iters":10})

    

    if alg_name == "HillClimb":
        search_strat = HillClimb(mutation_op)
    elif alg_name == "LocalSearch":
        search_strat = LocalSearch(mutation_op, {"iters":20})
    elif alg_name == "ES":
        search_strat = ES(mutation_op, cross_op, parent_sel_op, selection_op, {"popSize":100, "offspringSize":150})
    elif alg_name == "HS":
        search_strat = HS({"HMS":100, "HMCR":0.8, "BW":0.5, "PAR":0.2})
    elif alg_name == "GA":
        search_strat = GA(mutation_op, cross_op, parent_sel_op, selection_op, {"popSize":100, "pcross":0.8, "pmut":0.2})
    elif alg_name == "SA":
        search_strat = SA(mutation_op, {"iter":100, "temp_init":1, "alpha":0.997})
    elif alg_name == "DE":
        search_strat = DE(OperatorReal("DE/best/1", {"F":0.8, "Cr":0.8}), {"popSize":100})
    elif alg_name == "PSO":
        search_strat = PSO({"popSize":100, "w":0.7, "c1":1.5, "c2":1.5})
    elif alg_name == "NoSearch":
        search_strat = NoSearch({"popSize":100})
    else:
        print(f"Error: Algorithm \"{alg_name}\" doesn't exist.")
        exit()
    
    if memetic:
        alg = MemeticSearch(objfunc, search_strat, local_search, mem_select, pop_initializer, params=params)
    else:
        alg = GeneralSearch(objfunc, search_strat, pop_initializer, params=params)
    
    ind, fit = alg.optimize()
    print(ind)
    alg.display_report(show_plots=False)

    if save_state:
        alg.store_state("./examples/results/test.json", readable=True, show_pop=True)
        # show_best_solution=True,
        # show_fit_history=False, show_gen_history=False, show_pop=False, show_pop_details=False):


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algorithm", dest='alg', help='Specify an algorithm')
    parser.add_argument("-m", "--memetic", dest='mem', action="store_true", help='Does local search after mutation')
    parser.add_argument("-s", "--save-state", dest='save_state', action="store_true", help='Saves the state of the search strategy')
    args = parser.parse_args()

    algorithm_name = "ES"
    mem = False
    save_state = False

    if args.alg:
        algorithm_name = args.alg
    
    if args.mem:
        mem = True
    
    if args.save_state:
        save_state = True
   
    run_algorithm(alg_name = algorithm_name, memetic=mem, save_state=save_state)

if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     from pyevolcomp.BaseSearch import parse_stopping_cond, process_condition
#     a_str = "neval or ngen and time_limit or ngen and ngen"
#     parsed = parse_stopping_cond(a_str)
#     print(parsed)
#     print(process_condition(parsed, neval=True, ngen=True, real_time=True, target=True))