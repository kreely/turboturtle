#==================================================
# tt_variable.py - 2009-01-13
# The Variable class for Turbo Turtle
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

from tt_types import *

class Variable:
    def __init__(self, Name):
        self.Name = Name
        self.Type = ParamType.UNKNOWN
        self.ArrayDim = None
        self.CppName = None

    def SetType(self, Type):
        allowedtypes = (ParamType.UNKNOWN, ParamType.BOOLEAN, ParamType.NUMBER, ParamType.LISTNUM, ParamType.ARRAY, ParamType.QUOTEDWORD)
        if Type not in allowedtypes:
            return False
        self.Type = Type
        return True


