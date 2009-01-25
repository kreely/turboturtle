#==================================================
# tt_variable.py - 2009-01-13
# The Variable class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *

class Variable:
    def __init__(self, Name):
        self.Name = Name
        self.Type = ParamType.UNKNOWN
        self.CppName = None

    def SetType(self, Type):
        allowedtypes = (ParamType.UNKNOWN, ParamType.BOOLEAN, ParamType.NUMBER, ParamType.LISTNUM, ParamType.ARRAY, ParamType.QUOTEDWORD)
        if Type not in allowedtypes:
            return False
        self.Type = Type
        return True


