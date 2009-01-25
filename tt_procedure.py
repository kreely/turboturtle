#==================================================
# tt_procedure.py - 2009-01-13
# The Procedure class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

class Procedure:
    def __init__(self, Name, InputVars):
        self.CodeText = ""
        self.Name = Name
        self.ReturnType = ParamType.UNKNOWN
        self.InputVariables = []
        self.LocalVariables = []
        self.Instructions = []
        for varname in InputVars:
            newvar = Variable(varname)
            self.InputVariables.append(newvar)      # references to the new Variable object are stored in both
            self.LocalVariables.append(newvar)      # InputVariables and LocalVariables lists
        self.CppName = None
            
    def AddCode(self, SourceCode):
        self.CodeText = SourceCode

from tt_variable import *
from tt_types import *


