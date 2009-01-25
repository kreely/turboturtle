#==================================================
# tt_types.py - 2009-01-15
# Several type definitions for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

class ElemType:
    # static definitions for element types
    UNKNOWN = 0
    OPEN_PAREN = 1
    CLOSE_PAREN = 2
    OPEN_BRACKET = 3
    CLOSE_BRACKET = 4
    NUMBER = 5
    BOOLEAN = 6
    INFIX_NUM = 7
    INFIX_BOOL = 8
    QUOTED_WORD = 9
    VAR_VALUE = 10
    UNQUOT_WORD = 11
    FUNC_CALL = 11  # that's right, a function call and an unquoted word are the same
    CODE_LIST = 12

    Names = { UNKNOWN       : "Unknown",
              OPEN_PAREN    : "Open Parenthesis",
              CLOSE_PAREN   : "Close Parenthesis",
              OPEN_BRACKET  : "Open Bracket",
              CLOSE_BRACKET : "Close Bracket",
              NUMBER        : "Number",
              BOOLEAN       : "Boolean",
              INFIX_NUM     : "Numeric operator",
              INFIX_BOOL    : "Comparison operator",
              QUOTED_WORD   : "Quoted word",
              VAR_VALUE     : "Variable reference",
              FUNC_CALL     : "Function call",
              CODE_LIST     : "Code list" }

class ParamType:
    # procedure input/output parameter types
    UNKNOWN = 0
    NOTHING = 1
    ANYTHING = 2
    BOOLEAN = 3
    NUMBER = 4
    LISTCODE = 5
    LISTNUM = 6
    ARRAY = 7
    QUOTEDWORD = 8

    Names = { UNKNOWN    : "Unknown",
              NOTHING    : "Nothing",
              ANYTHING   : "Anything",
              BOOLEAN    : "Boolean",
              NUMBER     : "Number",
              LISTCODE   : "List of code",
              LISTNUM    : "List of numbers",
              ARRAY      : "Array",
              QUOTEDWORD : "Quoted word" }

class Struct(dict):
    def __getattr__(self,name):
        try:
            val = self[name]
        except KeyError:
            val = None
        return val
    def __setattr__(self,name,val):
        self[name] = val

