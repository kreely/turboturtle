#==================================================
# tt_builtin.py - 2009-01-13
# The Builtin class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *

class ProcParams:
    def __init__(self, name, abbrev, returntype, bParenform, bExtraargs, *ParmTypes):
        self.FullName = name
        self.AbbrevName = abbrev
        self.ReturnType = returntype
        self.ParamTypes = []
        for parmtype in ParmTypes:
            self.ParamTypes.append(parmtype)
        self.bParenthesized = bParenform
        self.bExtraArgs = bExtraargs
        self.nParams = len(self.ParamTypes)

class Builtin:
    # static data members
    _procs = []

    def AddBuiltin(cls, name, abbrev, returntype, bParenform, bExtraargs, *ParmTypes):
        newproc = ProcParams(name, abbrev, returntype, bParenform, bExtraargs, *ParmTypes)
        cls._procs.append(newproc)
    AddBuiltin = classmethod(AddBuiltin)

    def __init__(self):
        pass

        
# full built-in procedure table
Builtin.AddBuiltin(".setspecial",  None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.NUMBER)
Builtin.AddBuiltin("array",        None,    ParamType.ARRAY,   False, False, ParamType.NUMBER)
Builtin.AddBuiltin("back",         "bk",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("clean",        None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("clearscreen",  None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("for",          None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.NUMBER, ParamType.NUMBER, ParamType.LISTCODE)
Builtin.AddBuiltin("for",          None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.NUMBER, ParamType.NUMBER, ParamType.NUMBER, ParamType.LISTCODE)
Builtin.AddBuiltin("forever",      None,    ParamType.NOTHING, False, False, ParamType.LISTCODE)
Builtin.AddBuiltin("forward",      "fd",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("fput",         None,    ParamType.LISTNUM, False, False, ParamType.NUMBER,     ParamType.LISTNUM)
Builtin.AddBuiltin("left",         "lt",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("localmake",    None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.ANYTHING)
Builtin.AddBuiltin("lput",         None,    ParamType.LISTNUM, False, False, ParamType.NUMBER,     ParamType.LISTNUM)
Builtin.AddBuiltin("make",         None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.ANYTHING)
Builtin.AddBuiltin("mdarray",      None,    ParamType.ARRAY,   False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("output",       "op",    ParamType.NOTHING, False, False, ParamType.ANYTHING)
Builtin.AddBuiltin("penup",        "pu",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("pendown",      "pd",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("penerase",     "pe",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("penpaint",     "ppt",   ParamType.NOTHING, False, False)
Builtin.AddBuiltin("reverse",      None,    ParamType.LISTNUM, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("repcount",     "#",     ParamType.NUMBER,  False, False)
Builtin.AddBuiltin("repeat",       None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.LISTCODE)
Builtin.AddBuiltin("right",        "rt",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("setpensize",   None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setscrunch",   None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("stop",         None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("window",       None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("wrap",         None,    ParamType.NOTHING, False, False)


