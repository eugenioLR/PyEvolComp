from __future__ import annotations
from typing import Union
from copy import copy
import warnings
from ...ParamScheduler import ParamScheduler
from ...Algorithm import Algorithm
from ...Operator import Operator
from ...Operators import OperatorMeta
from ...SurvivorSelection import SurvivorSelection


class VNS(Algorithm):
    """
    Variable neighborhood search
    """

    def __init__(self, pop_init: Initializer, op_list: List[Operator], local_search = Algorithm, selection_op: SurvivorSelection = None, params: Union[ParamScheduler, dict] = {}, name: str = "VNS"):

        self.iterations = params["iters"] if "iters" in params else 100

        self.op_list = op_list
        self.perturb_op = OperatorMeta("Pick", op_list, {"init_idx": 0})

        self.local_search = local_search

        if selection_op is None:
            selection_op = SurvivorSelection("One-to-One")
        self.selection_op = selection_op

        if pop_init.pop_size > 1:
            pop_init.pop_size = 1
            warnings.warn("The VNS algorithm work on a single individual. The population size has been set to 1.", stacklevel=2)

        super().__init__(pop_init, params=params, name=name)
    
    def initialize(self, objfunc):
        super().initialize(objfunc)
        self.local_search.initialize(objfunc)

    def perturb(self, indiv_list, objfunc, progress=0, history=None):
        """
        Performs a step of the algorithm
        """
            
        offspring = []
        for indiv in indiv_list:

            # Perturb individual
            new_indiv = self.perturb_op(indiv, indiv_list, objfunc, self.best, self.pop_init)
            new_indiv.genotype = objfunc.repair_solution(new_indiv.genotype)

            # Local search
            population = [new_indiv]
            self.local_search.perturb_op = self.perturb_op
            for _ in range(self.iterations):
                parents, _ = self.local_search.select_parents(population, progress, history)

                offspring = self.local_search.perturb(parents, objfunc, progress, history)

                population = self.local_search.select_individuals(population, offspring, progress, history)
            
            new_indiv = self.local_search.population[0]

            offspring.append(new_indiv)

        # Keep best individual regardless of selection method
        current_best = max(offspring, key=lambda x: x.fitness)
        if self.best.fitness < current_best.fitness:
            self.best = current_best
        
        return offspring
    
    def select_individuals(self, population, offspring, progress=0, history=None):
        new_population = self.selection_op(population, offspring)

        if new_population[0].id == population[0].id:
            self.perturb_op.chosen_idx += 1
        else:
            self.perturb_op.chosen_idx = 0
        
        return new_population

    def update_params(self, progress):
        """
        Updates the parameters of each component of the algorithm
        """

        if isinstance(self.perturb_op, Operator):
            self.perturb_op.step(progress)
        
        if self.perturb_op.chosen_idx >= len(self.op_list) or self.perturb_op.chosen_idx < 0:
            self.perturb_op.chosen_idx = 0
    
    def extra_step_info(self):
        """
        Specific information to display relevant to this algorithm
        """

        idx = self.perturb_op.chosen_idx

        print(f"\tCurrent Operator: {idx}/{len(self.op_list)}, {self.op_list[idx].name}")