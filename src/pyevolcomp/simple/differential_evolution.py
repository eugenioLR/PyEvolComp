from __future__ import annotations
from ..Initializers import UniformVectorInitializer
from ..Operators import OperatorInt, OperatorReal, OperatorBinary
from ..Encodings import TypeCastEncoding
from ..ParentSelection import ParentSelection
from ..SurvivorSelection import SurvivorSelection
from ..Algorithms import DE
from ..SearchMethods import GeneralSearch

def differential_evolution(objfunc: ObjectiveVectorFunc, params: dict) -> Search:
    """
    Instantiates a differential evolution algorithm to optimize the given objective function.
    """

    encoding_str = params["encoding"] if "encoding" in params else "real"

    if encoding_str.lower() == "real":
        alg = _differential_evolution_real_vec(objfunc, params)
    elif encoding_str.lower() == "int":
        alg = _differential_evolution_int_vec(objfunc, params)
    elif encoding_str.lower() == "bin":
        alg = _differential_evolution_bin_vec(objfunc, params)
    else:
        raise ValueError(f"The encoding \"{encoding_str}\" does not exist, try \"real\", \"int\" or \"bin\"")
    
    return alg

def _differential_evolution_real_vec(objfunc, params):
    """
    Instantiates a differential evolution algorithm to optimize the given objective function.
    This objective function should accept real coded vectors.
    """

    pop_size = params["pop_size"] if "pop_size" in params else 100
    f = params["F"] if "F" in params else 0.8
    cr = params["Cr"] if "Cr" in params else 0.9
    de_type = params["DE_type"] if "DE_type" in params else "de/best/1"

    if de_type not in ["de/rand/1", "de/best/1", "de/rand/2", "de/best/2", "de/current-to-rand/1", "de/current-to-best/1", "de/current-to-pbest/1"]:
        raise ValueError(f"Differential evolution strategy \"{de_type}\" does not exist.")

    pop_initializer = UniformVectorInitializer(objfunc.vecsize, objfunc.low_lim, objfunc.up_lim, pop_size=pop_size, dtype=float)

    de_op = OperatorReal(de_type, {"F":f, "Cr":cr})
    
    search_strat = DE(pop_initializer, de_op)

    return GeneralSearch(objfunc, search_strat, params=params)


def _differential_evolution_int_vec(objfunc, params):
    """
    Instantiates a differential evolution algorithm to optimize the given objective function.
    This objective function should accept real coded vectors.
    """

    pop_size = params["pop_size"] if "pop_size" in params else 100
    f = params["F"] if "F" in params else 0.8
    cr = params["Cr"] if "Cr" in params else 0.9
    de_type = params["DE_type"] if "DE_type" in params else "de/best/1"

    if de_type not in ["de/rand/1", "de/best/1", "de/rand/2", "de/best/2", "de/current-to-rand/1", "de/current-to-best/1", "de/current-to-pbest/1"]:
        raise ValueError(f"Differential evolution strategy \"{de_type}\" does not exist.")

    encoding = TypeCastEncoding(float, int)

    pop_initializer = UniformVectorInitializer(objfunc.vecsize, objfunc.low_lim, objfunc.up_lim, pop_size=pop_size, dtype=float, encoding=encoding)

    de_op = OperatorReal(de_type, {"F":f, "Cr":cr})
    
    search_strat = DE(pop_initializer, de_op)

    return GeneralSearch(objfunc, search_strat, params=params)


def _differential_evolution_bin_vec(objfunc, params):
    """
    Instantiates a differential evolution algorithm to optimize the given objective function.
    This objective function should accept real coded vectors.
    """

    pop_size = params["pop_size"] if "pop_size" in params else 100
    f = params["F"] if "F" in params else 0.8
    cr = params["Cr"] if "Cr" in params else 0.9
    de_type = params["DE_type"] if "DE_type" in params else "de/best/1"

    if de_type not in ["de/rand/1", "de/best/1", "de/rand/2", "de/best/2", "de/current-to-rand/1", "de/current-to-best/1", "de/current-to-pbest/1"]:
        raise ValueError(f"Differential evolution strategy \"{de_type}\" does not exist.")

    encoding = TypeCastEncoding(float, bool)

    pop_initializer = UniformVectorInitializer(objfunc.vecsize, objfunc.low_lim, objfunc.up_lim, pop_size=pop_size, dtype=float, encoding=encoding)

    de_op = OperatorReal(de_type, {"F":f, "Cr":cr})
    
    search_strat = DE(pop_initializer, de_op)

    return GeneralSearch(objfunc, search_strat, params=params)
