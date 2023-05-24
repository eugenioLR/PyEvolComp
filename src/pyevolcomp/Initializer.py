from __future__ import annotations
from abc import ABC, abstractmethod
from .Encodings import DefaultEncoding


class Initializer(ABC):
    """
    Abstract population initializer class
    """

    def __init__(self, pop_size: int = 1, encoding: Encoding = None):
        self.pop_size = pop_size
        if encoding is None:
            encoding = DefaultEncoding()
        self.encoding = encoding
    
    @abstractmethod
    def generate_random(self, objfunc: ObjectiveFunc) -> Individual:
        """
        Generates a random individual
        """
    
    def generate_individual(self, objfunc: ObjectiveFunc) -> Individual:
        """
        Define how an individual is initialized
        """

        return self.generate_random(objfunc)
    
    def generate_population(self, objfunc: ObjectiveFunc, n_indiv: int = None) -> List[Individual]:
        """
        Generate n_indiv Individuals using the generate_individual method.
        """
        
        if n_indiv is None:
            n_indiv = self.pop_size
        
        return [self.generate_individual(objfunc) for i in range(n_indiv)]
