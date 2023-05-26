from __future__ import annotations
import numpy as np
from .ES import ES
from typing import Union, List
from copy import copy
from ..Individual import Individual
from ..Operators import OperatorReal, OperatorMeta
from ..SurvivorSelection import SurvivorSelection
from ..ParentSelection import ParentSelection
from .StaticPopulation import StaticPopulation
from .HillClimb import HillClimb
from ..ParamScheduler import ParamScheduler


class HS(ES):
    def __init__(self, pop_init: Initializer, params: Union[ParamScheduler, dict] = {}, name: str = "HS"):

        params["offspringSize"] = 1

        parent_select = ParentSelection("Nothing")
        selection = SurvivorSelection("(m+n)")

        HSM = pop_init.pop_size
        cross = OperatorReal("Multicross", {"Nindiv": HSM})

        mutate1 = OperatorReal("MutNoise", {"method": "Gauss", "F": params["BW"], "Cr": params["HMCR"] * params["PAR"]})
        rand1 = OperatorReal("RandomMask", {"Cr": 1 - params["HMCR"]})

        mutate = OperatorMeta("Sequence", [mutate1, rand1])

        super().__init__(pop_init, mutate, cross, parent_select, selection, params, name=name)


class DE(StaticPopulation):
    def __init__(self, pop_init: Initializer, de_op: Operator, params: Union[ParamScheduler, dict] = {}, selection_op: SurvivorSelection = None, name: str = "DE"):
        if selection_op is None:
            selection_op = SurvivorSelection("One-to-one")

        super().__init__(pop_init, de_op, params, selection_op, name=name)


class PSO(StaticPopulation):
    def __init__(self, pop_init: Initializer, params: Union[ParamScheduler, dict] = {}, pso_op: Operator = None, name: str = "PSO"):
        if pso_op is None:
            w = params["w"] if "w" in params else 0.7
            c1 = params["c1"] if "c1" in params else 1.5
            c2 = params["c2"] if "c2" in params else 1.5
            pso_op = OperatorReal("PSO", ParamScheduler("Linear", {"w": w, "c1": c1, "c2": c2}))

        selection_op = SurvivorSelection("Generational")

        super().__init__(pop_init, pso_op, params, selection_op, name=name)

    def extra_step_info(self):
        """
        Specific information to display relevant to this algorithm
        """

        popul_matrix = np.array(list(map(lambda x: x.genotype, self.population)))
        speed_matrix = np.array(list(map(lambda x: x.speed, self.population)))
        divesity = popul_matrix.std(axis=1).mean()
        mean_speed = speed_matrix.mean()
        print(f"\tdiversity: {divesity:0.3}")
        print(f"\tmean speed: {mean_speed:0.3}")


class CRO(StaticPopulation):
    def __init__(self, pop_init: Initializer, mutate: Operator, cross: Operator, params: Union[ParamScheduler, dict] = {}, name: str = "CRO"):

        evolve_op = OperatorMeta("Branch", [cross, mutate], {"p": params["Fb"]})

        selection_op = SurvivorSelection("CRO", {"Fd": params["Fd"], "Pd": params["Pd"], "attempts": params["attempts"], "maxPopSize": params["popSize"]})
        
        params = copy(params)
        params["popSize"] = round(params["popSize"] * params["rho"])
        
        super().__init__(pop_init, evolve_op, params, selection_op, name=name)


class NoSearch(StaticPopulation):
    """
    Debug Algorithm that does nothing
    """

    def __init__(self, pop_init: Initializer, params: Union[ParamScheduler, dict] = {}, name: str = "No search"):
        noop = OperatorReal("Nothing")
        selection_op = SurvivorSelection("Generational")
        super().__init__(pop_init, noop, params, selection_op, name=name)

    def perturb(self, parent_list, pop_init, objfunc, progress=0, history=None):
        return parent_list


class RandomSearch(HillClimb):
    def __init__(self, pop_init, name="RandomSearch"):
        op = OperatorReal("Random", {})
        super().__init__(pop_init, op, name=name)


