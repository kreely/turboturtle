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
Builtin.AddBuiltin("abs",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("and",          None,    ParamType.BOOLEAN, False, False, ParamType.BOOLEAN,    ParamType.BOOLEAN)
Builtin.AddBuiltin("and",          None,    ParamType.BOOLEAN, True,  True,  ParamType.BOOLEAN)
Builtin.AddBuiltin("arctan",       None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("arctan",       None,    ParamType.NUMBER,  True,  False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("array",        None,    ParamType.ARRAY,   False, False, ParamType.NUMBER)
Builtin.AddBuiltin("array",        None,    ParamType.ARRAY,   True,  False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("back",         "bk",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("butfirst",     None,    ParamType.LISTNUM, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("butlast",      None,    ParamType.LISTNUM, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("clean",        None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("clearscreen",  "cs",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("cos",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("count",        None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("difference",   None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("do.while",     None,    ParamType.NOTHING, False, False, ParamType.LISTCODE,   ParamType.BOOLEAN)
Builtin.AddBuiltin("do.until",     None,    ParamType.NOTHING, False, False, ParamType.LISTCODE,   ParamType.BOOLEAN)
Builtin.AddBuiltin("dot",          None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("emptyp",       None,    ParamType.BOOLEAN, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("erasescreen",  None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("exp",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("first",        None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("for",          None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.NUMBER, ParamType.NUMBER, ParamType.LISTCODE)
Builtin.AddBuiltin("for",          None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.NUMBER, ParamType.NUMBER, ParamType.NUMBER, ParamType.LISTCODE)
Builtin.AddBuiltin("forever",      None,    ParamType.NOTHING, False, False, ParamType.LISTCODE)
Builtin.AddBuiltin("forward",      "fd",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("fput",         None,    ParamType.LISTNUM, False, False, ParamType.NUMBER,     ParamType.LISTNUM)
Builtin.AddBuiltin("gaussian",     None,    ParamType.NUMBER,  False, False)
Builtin.AddBuiltin("goto",         None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD)
Builtin.AddBuiltin("heading",      None,    ParamType.NUMBER,  False, False)
Builtin.AddBuiltin("home",         None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("if",           None,    ParamType.NOTHING, False, False, ParamType.BOOLEAN,    ParamType.LISTCODE)
Builtin.AddBuiltin("ifelse",       None,    ParamType.NOTHING, False, False, ParamType.BOOLEAN,    ParamType.LISTCODE, ParamType.LISTCODE)
Builtin.AddBuiltin("iftrue",       "ift",   ParamType.NOTHING, False, False, ParamType.LISTCODE)
Builtin.AddBuiltin("iffalse",      "iff",   ParamType.NOTHING, False, False, ParamType.LISTCODE)
Builtin.AddBuiltin("int",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("item",         None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.LISTNUM)
Builtin.AddBuiltin("item",         None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.ARRAY)
Builtin.AddBuiltin("label",        None,    ParamType.NOTHING, True,  True,  ParamType.ANYTHING)
Builtin.AddBuiltin("last",         None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("left",         "lt",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("list",         None,    ParamType.LISTNUM, False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("list",         None,    ParamType.LISTNUM, True,  True,  ParamType.NUMBER)
Builtin.AddBuiltin("localmake",    None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.ANYTHING)
Builtin.AddBuiltin("log10",        None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("ln",           None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("lput",         None,    ParamType.LISTNUM, False, False, ParamType.NUMBER,     ParamType.LISTNUM)
Builtin.AddBuiltin("make",         None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD, ParamType.ANYTHING)
Builtin.AddBuiltin("mdarray",      None,    ParamType.ARRAY,   False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("mditem",       None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM,    ParamType.ARRAY)
Builtin.AddBuiltin("mdsetitem",    None,    ParamType.NOTHING, False, False, ParamType.LISTNUM,    ParamType.ARRAY, ParamType.NUMBER)
Builtin.AddBuiltin("minus",        None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("not",          None,    ParamType.BOOLEAN, False, False, ParamType.BOOLEAN)
Builtin.AddBuiltin("or",           None,    ParamType.BOOLEAN, False, False, ParamType.BOOLEAN,    ParamType.BOOLEAN)
Builtin.AddBuiltin("or",           None,    ParamType.BOOLEAN, True,  True,  ParamType.BOOLEAN)
Builtin.AddBuiltin("output",       "op",    ParamType.NOTHING, False, False, ParamType.ANYTHING)
Builtin.AddBuiltin("penup",        "pu",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("pendown",      "pd",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("penerase",     "pe",    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("penpaint",     "ppt",   ParamType.NOTHING, False, False)
Builtin.AddBuiltin("pick",         None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("pos",          None,    ParamType.LISTNUM, False, False)
Builtin.AddBuiltin("power",        None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("print",        None,    ParamType.NOTHING, True,  True,  ParamType.ANYTHING)
Builtin.AddBuiltin("product",      None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("product",      None,    ParamType.NUMBER,  True,  True,  ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("quotient",     None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("quotient",     None,    ParamType.NUMBER,  True,  False, ParamType.NUMBER)
Builtin.AddBuiltin("radarctan",    None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("radarctan",    None,    ParamType.NUMBER,  True,  False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("radcos",       None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("radsin",       None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("random",       None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("random",       None,    ParamType.NUMBER,  True,  False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("remainder",    None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("repcount",     "#",     ParamType.NUMBER,  False, False)
Builtin.AddBuiltin("repeat",       None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.LISTCODE)
Builtin.AddBuiltin("rerandom",     None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("rerandom",     None,    ParamType.NOTHING, True,  False, ParamType.NUMBER)
Builtin.AddBuiltin("reverse",      None,    ParamType.LISTNUM, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("right",        "rt",    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("round",        None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setbackground","setbg", ParamType.NOTHING, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("setfont",      None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setfontheight",None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setheading",   "seth",  ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setitem",      None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.ARRAY, ParamType.NUMBER)
Builtin.AddBuiltin("setjustifyvert",None,   ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setjustifyhorz",None,   ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setpencolor",  "setpc", ParamType.NOTHING, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("setpensize",   None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("setpos",       None,    ParamType.NOTHING, False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("setscrunch",   None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("setxy",        None,    ParamType.NOTHING, False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("setx",         None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("sety",         None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("sin",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("sqrt",         None,    ParamType.NUMBER,  False, False, ParamType.NUMBER)
Builtin.AddBuiltin("stop",         None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("sum",          None,    ParamType.NUMBER,  False, False, ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("sum",          None,    ParamType.NUMBER,  True,  True,  ParamType.NUMBER,     ParamType.NUMBER)
Builtin.AddBuiltin("tag",          None,    ParamType.NOTHING, False, False, ParamType.QUOTEDWORD)
Builtin.AddBuiltin("test",         None,    ParamType.NOTHING, False, False, ParamType.BOOLEAN)
Builtin.AddBuiltin("towards",      None,    ParamType.NUMBER,  False, False, ParamType.LISTNUM)
Builtin.AddBuiltin("until",        None,    ParamType.NOTHING, False, False, ParamType.BOOLEAN,    ParamType.LISTCODE)
Builtin.AddBuiltin("wait",         None,    ParamType.NOTHING, False, False, ParamType.NUMBER)
Builtin.AddBuiltin("while",        None,    ParamType.NOTHING, False, False, ParamType.BOOLEAN,    ParamType.LISTCODE)
Builtin.AddBuiltin("window",       None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("wrap",         None,    ParamType.NOTHING, False, False)
Builtin.AddBuiltin("xcor",         None,    ParamType.NUMBER,  False, False)
Builtin.AddBuiltin("ycor",         None,    ParamType.NUMBER,  False, False)


