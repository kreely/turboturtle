#==================================================
# tt_builtin.py - 2009-01-13
# The Builtin class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *

class ProcParams:
    def __init__(self, name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extraargs):
        self.FullName = name
        self.AbbrevName = abbrev
        self.ReturnType = returntype
        self.ParamTypes = (parm1type, parm2type, parm3type)
        self.bParenthesized = parenform
        self.bExtraArgs = extraargs
        self.nParams = len([parm for parm in self.ParamTypes if parm is not None])

class Builtin:
    # static data members
    _procs = []

    def AddBuiltin(cls, name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extraargs):
        newproc = ProcParams(name, abbrev, returntype, parm1type, parm2type, parm3type, parenform, extraargs)
        cls._procs.append(newproc)
    AddBuiltin = classmethod(AddBuiltin)

    def __init__(self):
        pass

        
# full built-in procedure table
Builtin.AddBuiltin("array",        None,    ParamType.ARRAY,   ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("back",         "bk",    ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("clean",        None,    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("clearscreen",  None,    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("forever",      None,    ParamType.NOTHING, ParamType.LISTCODE,   None,               None, False, False)
Builtin.AddBuiltin("forward",      "fd",    ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("fput",         None,    ParamType.LISTNUM, ParamType.NUMBER,     ParamType.LISTNUM,  None, False, False)
Builtin.AddBuiltin("left",         "lt",    ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("localmake",    None,    ParamType.NOTHING, ParamType.QUOTEDWORD, ParamType.ANYTHING, None, False, False)
Builtin.AddBuiltin("lput",         None,    ParamType.LISTNUM, ParamType.NUMBER,     ParamType.LISTNUM,  None, False, False)
Builtin.AddBuiltin("make",         None,    ParamType.NOTHING, ParamType.QUOTEDWORD, ParamType.ANYTHING, None, False, False)
Builtin.AddBuiltin("mdarray",      None,    ParamType.ARRAY,   ParamType.LISTNUM,    None,               None, False, False)
Builtin.AddBuiltin("penup",        "pu",    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("pendown",      "pd",    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("penerase",     "pe",    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("penpaint",     "ppt",   ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("penreverse",   "px",    ParamType.NOTHING, None,                 None,               None, False, False)
Builtin.AddBuiltin("reverse",      None,    ParamType.LISTNUM, ParamType.LISTNUM,    None,               None, False, False)
Builtin.AddBuiltin("repcount",     "#",     ParamType.NUMBER,  None,                 None,               None, False, False)
Builtin.AddBuiltin("repeat",       None,    ParamType.NOTHING, ParamType.NUMBER,     ParamType.LISTCODE, None, False, False)
Builtin.AddBuiltin("right",        "rt",    ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, ParamType.LISTNUM,    None,               None, False, False)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, ParamType.LISTNUM,    None,               None, False, False)
Builtin.AddBuiltin("setpensize",   None,    ParamType.NOTHING, ParamType.NUMBER,     None,               None, False, False)


