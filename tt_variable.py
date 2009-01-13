#==================================================
# tt_variable.py - 2009-01-13
# The Variable class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

class Variable:
    # define variable types
    UNKNOWN = 0
    NUMBER = 1
    LIST = 2
    ARRAY = 3
    
    def __init__(self, Name):
        self.Name = Name
        self.Type = Variable.UNKNOWN

