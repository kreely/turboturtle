#==================================================
# tt_procedure.py - 2009-01-13
# The Procedure class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken (Richard@fascinationsoftware.com)
#--------------------------------------------------

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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


