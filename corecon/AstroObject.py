import numpy as np
import copy

from .DataEntryClass import DataEntry
from .FieldClass import Field

#####################
# AstroObject Class #
#####################

class AstroObject():
    def __init__(self):
        """construct method
        """
        self._unique_id = get_last_unique_id()
        self.identifiers = []

    def __repr__(self):
        """string describing the class
        """
        return "corecon AstroObject class"

    def __str__(self):
        """output of print
        """
        ostr=""
        ostr+="identifiers:\n"
        for ident in self.identifiers:
            ostr+=f"  {str(ident)}\n"

        return ostr

    def __eq__(self,other):
        """custom equality definition
        """
        return self.unique_id == other.unique_id
    


