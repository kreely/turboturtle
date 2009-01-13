#==================================================
# tt_procedure.py - 2009-01-13
# The Procedure class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_variable import *

class Procedure:
    def __init__(self, Name, InputVars):
        self.CodeText = ""
        self.Name = Name
        self.InputVariables = []
        for varname in InputVars:
            newvar = Variable(varname)
            self.InputVariables.append(newvar)
            
    def AddCode(self, SourceCode):
        self.CodeText = SourceCode
