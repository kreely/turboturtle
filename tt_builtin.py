#==================================================
# tt_builtin.py - 2009-01-13
# The Builtin class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *

class ProcParams:
    def __init__(self, name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extranums):
        self.FullName = name
        self.AbbrevName = abbrev
        self.ReturnType = returntype
        self.Param1Type = parm1type
        self.Param2Type = parm2type
        self.Param3Type = parm3type
        self.bParenthesized = parenform
        self.bExtraNumbers = extranums
        self.nParams = 0
        if self.Param1Type is not None:
            self.nParams += 1
        if self.Param2Type is not None:
            self.nParams += 1
        if self.Param3Type is not None:
            self.nParams += 1

class Builtin:
    # static data members
    _procs = []

    def AddBuiltin(cls, name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extranums):
        newproc = ProcParams(name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extranums)
        cls._procs.append(newproc)
    AddBuiltin = classmethod(AddBuiltin)

    def __init__(self):
        pass

        
# full built-in procedure table
Builtin.AddBuiltin("array",        None,    ParamType.ARRAY,   ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("back",         "bk",    ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("clean",        None,    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("clearscreen",  None,    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("forever",      None,    ParamType.NOTHING, ParamType.LISTCODE, None,               None, False, False)
Builtin.AddBuiltin("forward",      "fd",    ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("fput",         None,    ParamType.LISTNUM, ParamType.NUMBER,   ParamType.LISTNUM,  None, False, False)
Builtin.AddBuiltin("left",         "lt",    ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("lput",         None,    ParamType.LISTNUM, ParamType.NUMBER,   ParamType.LISTNUM,  None, False, False)
Builtin.AddBuiltin("mdarray",      None,    ParamType.ARRAY,   ParamType.LISTNUM,  None,               None, False, False)
Builtin.AddBuiltin("penup",        "pu",    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("pendown",      "pd",    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("penerase",     "pe",    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("penpaint",     "ppt",   ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("penreverse",   "px",    ParamType.NOTHING, None,               None,               None, False, False)
Builtin.AddBuiltin("reverse",      None,    ParamType.LISTNUM, ParamType.LISTNUM,  None,               None, False, False)
Builtin.AddBuiltin("repcount",     "#",     ParamType.NUMBER,  None,               None,               None, False, False)
Builtin.AddBuiltin("repeat",       None,    ParamType.NOTHING, ParamType.NUMBER,   ParamType.LISTCODE, None, False, False)
Builtin.AddBuiltin("right",        "rt",    ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, ParamType.LISTNUM,  None,               None, False, False)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, ParamType.LISTNUM,  None,               None, False, False)
Builtin.AddBuiltin("setpensize",   None,    ParamType.NOTHING, ParamType.NUMBER,   None,               None, False, False)


