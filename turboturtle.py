#!/usr/bin/env python
#==================================================
# TurboTurtle.py - 2009-01-13
# A Logo to C++ translator for fast Turtle Graphics
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

import os, sys
from tt_types import *
from tt_variable import *
from tt_procedure import *
from tt_parser import *
from tt_builtin import *
from tt_instruction import *

def main():
    # check the input parameters
    if len(sys.argv) < 3:
        printhelp()
        print "Error: Not enough input arguments"
        return
    if not os.path.isfile(sys.argv[1]):
        printhelp()
        print "Error: input file \"%s\" does not exist" % sys.argv[1]
        return
    # create an application object and run it
    app = TT_App(sys.argv[1], sys.argv[2])
    app.Run()
    # All Done

def printhelp():
    print "TurboTurtle - A Logo to C++ translator for fast Turtle Graphics"
    print "Usage: %s InputFile OutputFile" % sys.argv[0]
    print "       InputFile - a Logo source code file to be translated"
    print "       OutputFile - a C++ source code file to be compiled and linked with the TurboTurtle graphics core"
    print

class TT_App:
    def __init__(self, InputName, OutputName):
        self.InputName = InputName
        self.OutputName = OutputName

    def Run(self):
        # start by loading the input source code
        f = open(self.InputName, 'r')
        InputCodeRaw = f.read()
        f.close()
        # do first pass parsing to remove any comments and handle line continuations
        self.InputCode = Parser.RemoveCommentsContinueLines(InputCodeRaw)
        # the second pass extracts the defined procedures and removes linefeeds to make streams of instructions
        (self.MainCode, self.Procedures) = Parser.ExtractProcedures(self.InputCode)
        if self.MainCode == None or self.Procedures == None:
            return
        # the next step is to parse instructions for the main code and the subroutines
        self.MainInstructions = Parser.ParseInstructions(self.MainCode, None, self.Procedures)
        if self.MainInstructions is None:
            return
        for proc in self.Procedures:
            proc.Instructions = Parser.ParseInstructions(proc.CodeText, proc.Name, self.Procedures)
            if proc.Instructions is None:
                return
        # fixme debug
        print "Main Code: %s\nMain Instructions:" % self.MainCode
        for instruct in self.MainInstructions:
            self.InstructPrint(instruct, 0)
        for proc in self.Procedures:
            print "Procedure '%s':" % proc.Name
            print "    Inputs: %s" % ",".join([var.Name for var in proc.InputVariables])
            print "    Code: %s" % proc.CodeText
            print "    Instructions:"
            for instruct in proc.Instructions:
                self.InstructPrint(instruct, 0)

    def InstructPrint(self, instruct, indent):
        print " " * indent + "Name: %s" % instruct.Name
        indent += 4
        for arg in instruct.Arguments:
            print " " * indent + "Arg: ",
            for i in range(arg.nElem):
                print "<%s> " % arg.ElemText[i],
                if arg.ElemTypes[i] == ElemType.FUNC_CALL:
                    self.PrintInstruction(arg.ElemInstr[i], indent + 4)
            print
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.ElemInstr:
                    self.PrintInstruction(instr, indent + 4)

# this function is executed when this script is run (not imported)
if __name__ == '__main__':
    # run the main function at the top of this source file
    main()

