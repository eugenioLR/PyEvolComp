from __future__ import annotations
from collections.abc import Iterable
import random
from ..Operator import Operator
from copy import copy, deepcopy
import numpy as np
import enum
from enum import Enum
from ..utils import RAND_GEN


class MetaOpMethods(Enum):
    BRANCH = enum.auto()
    SEQUENCE = enum.auto()
    SPLIT = enum.auto()
    PICK = enum.auto()

    @staticmethod
    def from_str(str_input):
        str_input = str_input.lower()

        if str_input not in meta_ops_map:
            raise ValueError(f'Operator on operators "{str_input}" not defined')

        return meta_ops_map[str_input]


meta_ops_map = {
    "branch": MetaOpMethods.BRANCH,
    "sequence": MetaOpMethods.SEQUENCE,
    "split": MetaOpMethods.SPLIT,
    "pick": MetaOpMethods.PICK,
}


class OperatorMeta(Operator):
    """
    Operator class that utilizes a list of operators to modify individuals.

    Parameters
    ----------
    method: str
        Type of operator that will be applied.
    op_list: List[Operator]
        List of operators that will be used.
    params: ParamScheduler or dict, optional
        Dictionary of parameters to define the operator.
    name: str, optional
        Name that is associated with the operator.
    """

    def __init__(
        self,
        method: str,
        op_list: List[Operator],
        params: Union[ParamScheduler, dict] = None,
        name: str = None,
    ):
        """
        Constructor for the OperatorMeta class
        """

        self.op_list = op_list

        if params is None:
            # Default parameters
            params = {
                "p": 0.5,
                "weights": [1] * len(op_list),
                "mask": 0,
                "init_idx": -1,
            }

        if name is None:
            op_names = []
            for op in op_list:
                if not isinstance(op, Operator):
                    op_names.append("lambda_func")
                else:
                    op_names.append(op.name)

            joined_names = ", ".join(op_names)
            name = f"{method}({joined_names})"

        super().__init__(params, name)

        self.method = MetaOpMethods.from_str(method)

        # Record of the index of the last operator used
        self.chosen_idx = params.get("init_idx", -1)
        self.mask = params.get("mask", 0)

        # If we have a branch with 2 operators and "p" is given as an input
        if self.method == MetaOpMethods.BRANCH and "weights" not in params and "p" in params and len(op_list) == 2:
            params["weights"] = [params["p"], 1 - params["p"]]
    
    def evolve(self, population, initializer=None, global_best=None):
        new_population = None
        population_matrix = copy(population.genotype_set)
        fitness_array = population.fitness

        if self.method == MetaOpMethods.BRANCH:
            self.chosen_idx = RAND_GEN.choice(np.arange(len(self.op_list)), size=len(population.genotype_set), p=self.params["weights"])
            population_matrix = population.genotype_set
            speed = population.speed_set
            for idx, op in enumerate(self.op_list):
                split_mask = self.chosen_idx == idx

                if np.any(split_mask):
                    split_population = population.update_genotype_set(population_matrix[split_mask], speed[split_mask]) 
                    split_population = op.evolve(split_population, global_best, initializer)

                    population_matrix[split_mask, :] = split_population.genotype_set
                    speed[split_mask, :] = split_population.speed_set

        elif self.method == MetaOpMethods.PICK:
            if isinstance(self.chosen_idx, np.ndarray) and self.chosen_idx.ndim > 0:
                chosen_idx = self.chosen_idx
            else:
                chosen_idx = np.asarray([self.chosen_idx]*len(population))

            # the chosen index is assumed to be changed by the user
            population_matrix = population.genotype_set
            speed = population.speed_set
            for idx, op in enumerate(self.op_list):
                split_mask = chosen_idx == idx

                if np.any(split_mask):
                    split_population = population.update_genotype_set(population_matrix[split_mask], speed[split_mask]) 
                    split_population = op.evolve(split_population, global_best, initializer)

                    population_matrix[split_mask, :] = split_population.genotype_set
                    speed[split_mask, :] = split_population.speed_set

        elif self.method == MetaOpMethods.SEQUENCE:
            new_population = copy(population)
            for op in self.op_list:
                new_population = op.evolve(new_population, global_best, initializer)

        elif self.method == MetaOpMethods.SPLIT:

            # for idx_op, op in enumerate(self.op_list):
            #     curr_mask = self.mask == idx_op 
            #     if np.any(curr_mask):
            #         filtered_best = self._filter_indiv(global_best, curr_mask)
            #         split_population = [self._filter_indiv(indiv, curr_mask) for indiv in population]
            #         split_population = op.evolve(population, objfunc, filtered_best, initializer)
            #         population = [self._undo_filter_indiv(indiv, filtered_indiv, curr_mask) for indiv, filtered_indiv in zip(population, split_population)]
            
            population_matrix = population.genotype_set
            speed = population.speed_set
            for idx_op, op in enumerate(self.op_list):
                split_mask = self.mask == idx_op 

                if np.any(split_mask):
                    split_population = population.update_genotype_set(population_matrix[:, split_mask], speed[:, split_mask]) 
                    split_population = op.evolve(split_population, global_best, initializer)

                    population_matrix[:, split_mask] = split_population.genotype_set
                    speed[:, split_mask] = split_population.speed_set


        if new_population is None:
            new_population = population.update_genotype_set(population_matrix, speed)
        
        return new_population

    def evolve_single(self, indiv, population, objfunc, initializer=None, global_best=None, indiv_idx=0):
        if self.method == MetaOpMethods.BRANCH:
            self.chosen_idx = random.choices(range(len(self.op_list)), k=1, weights=self.params["weights"])[0]
            chosen_op = self.op_list[self.chosen_idx]
            result = chosen_op.evolve_single(indiv, population, objfunc, global_best, initializer)

        elif self.method == MetaOpMethods.PICK:
            # the chosen index is assumed to be changed by the user
            if not isinstance(self.chosen_idx, Iterable):
                chosen_op = self.op_list[self.chosen_idx[indiv_idx]]
            else:
                chosen_op = self.op_list[self.chosen_idx]
            result = chosen_op.evolve_single(indiv, population, objfunc, global_best, initializer)

        elif self.method == MetaOpMethods.SEQUENCE:
            result = indiv
            for op in self.op_list:
                result = op.evolve_single(result, population, objfunc, global_best, initializer)

        elif self.method == MetaOpMethods.SPLIT:
            result = copy(indiv)
            indiv_copy = copy(indiv)
            global_best_copy = copy(global_best)
            population_copy = [copy(i) for i in population]

            for idx_op, op in enumerate(self.op_list):
                if np.any(self.mask == idx_op):
                    indiv_copy.genotype = indiv.genotype[self.mask == idx_op]
                    global_best_copy.genotype = global_best.genotype[self.mask == idx_op]

                    for idx_pop, val in enumerate(population_copy):
                        val.genotype = population[idx_pop].genotype[self.mask == idx_op]

                    aux_indiv = op.evolve_single(indiv_copy, population_copy, objfunc, global_best, initializer)
                    result.genotype[self.mask == idx_op] = aux_indiv.genotype

        return result
    
    @staticmethod
    def _filter_indiv(indiv, mask):
        indiv_copy = copy(indiv)
        if indiv is not None:
            indiv_copy.genotype = indiv.genotype[mask]
            indiv_copy.best = indiv.best[mask]
            indiv_copy.speed = indiv.speed[mask]
        return indiv_copy
    
    @staticmethod
    def _undo_filter_indiv(indiv, filtered_indiv, mask):
        if indiv is not None:
            indiv.genotype[mask] = filtered_indiv.genotype
            indiv.speed[mask] = filtered_indiv.speed
        return indiv

    def step(self, progress: float):
        super().step(progress)

        for op in self.op_list:
            if isinstance(op, Operator):
                op.step(progress)

    def get_state(self) -> dict:
        data = super().get_state()

        data["op_list"] = []

        for op in self.op_list:
            if isinstance(op, Operator):
                data["op_list"].append(op.get_state())
            else:
                data["op_list"].append("lambda_func")

        return data
