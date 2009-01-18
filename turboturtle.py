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
        self.MainInstructions = TT_App.ParseInstructions(self.MainCode, None, self.Procedures)
        if self.MainInstructions is None:
            return
        for proc in self.Procedures:
            proc.Instructions = TT_App.ParseInstructions(proc.CodeText, proc.Name, self.Procedures)
            if proc.Instructions is None:
                return
        # create local/global variables from MAKE instructions
        self.GlobalVariables = []
        for instruct in self.MainInstructions:
            if not TT_App.RecurseInstruction(TT_App.CreateVarFromInstruct, instruct, None, self.GlobalVariables, None):
                return
        for proc in self.Procedures:
            for instruct in proc.Instructions:
                if not TT_App.RecurseInstruction(TT_App.CreateVarFromInstruct, instruct, proc.Name, self.GlobalVariables, proc.LocalVariables):
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

    # instruction recursion loop, accepting a function to call for each instruction
    @staticmethod
    def RecurseInstruction(pFunction, instruct, *extraargs):
        # call the given function
        if not pFunction(instruct, *extraargs):
            return False
        # recurse through other instructions
        for arg in instruct.Arguments:
            for i in range(arg.nElem):
                if arg.ElemTypes[i] == ElemType.FUNC_CALL:
                    if not TT_App.RecurseInstruction(pFunction, arg.ElemInstr[i], *extraargs):
                        return False
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.ElemInstr:
                    if not TT_App.RecurseInstruction(pFunction, instr, *extraargs):
                        return False
        return True

    # debug function
    def InstructPrint(self, instruct, indent):
        print " " * indent + "Name: %s" % instruct.Name
        indent += 4
        for arg in instruct.Arguments:
            print " " * indent + "Arg: ",
            for i in range(arg.nElem):
                print "<%s> " % arg.ElemText[i],
                if arg.ElemTypes[i] == ElemType.FUNC_CALL:
                    self.InstructPrint(arg.ElemInstr[i], indent + 4)
            print
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.ElemInstr:
                    self.InstructPrint(instr, indent + 4)

    # functions for parsing Instruction objects out of code text
    @staticmethod
    def ParseInstructions(CodeText, ProcName, Procedures):
        # parse the instruction stream into a list of elements
        Elements = Parser.ParseStreamElements(CodeText, ProcName)
        if Elements is None:
            return None
        # pull instructions out of the element list
        Instructions = []
        while len(Elements) > 0:
            instruction = Parser.GetSingleInstruction(Elements, ProcName, Procedures)
            if instruction is None:
                return None
            # parse the Instruction lists in procedure arguments
            if not TT_App.RecurseInstruction(TT_App.ParseInstructionsInArgs, instruction, ProcName, Procedures):
                return None
            Instructions.append(instruction)
        # for instr in Instructions:
        return Instructions

    @staticmethod
    def ParseInstructionsInArgs(Instruct, ProcName, Procedures):
        for arg in Instruct.Arguments:
            if arg.ArgType == ParamType.LISTCODE:
                # convert the list (without brackets) back to text, and re-read the elements as a new instructions
                codelisttext = " ".join(arg.ElemText)
                codelistelems = Parser.ParseStreamElements(codelisttext, ProcName)
                # pull instructions out of the element list
                instr_codelist = []
                while len(codelistelems) > 0:
                    instruction = Parser.GetSingleInstruction(codelistelems, ProcName, Procedures)
                    if instruction is None:
                        return False
                    instr_codelist.append(instruction)
                # store this list of instructions in this argument.  this removes the original element lists
                arg.nElem = 1
                arg.ElemTypes = [ ElemType.CODE_LIST ]
                arg.ElemText = [ codelisttext ]
                arg.ElemInstr = instr_codelist
        return True

    # functions to allocate a global or local variable from a MAKE or LOCALMAKE procedure call
    @staticmethod
    def CreateVarFromInstruct(Instruct, ProcName, GlobalVariables, LocalVariables):
        if Instruct.Name.lower() == 'make':
            if not TT_App.CreateVar(Instruct, ProcName, GlobalVariables):
                return False
        elif Instruct.Name.lower() == 'localmake':
            if ProcName is None or LocalVariables is None:
                print "Syntax error: LOCALMAKE used outside of procedure definition"
                return False
            if not TT_App.CreateVar(Instruct, ProcName, LocalVariables):
                return False
        return True
    @staticmethod
    def CreateVar(Instruct, ProcName, VarList):
        ErrProcName = ProcName or 'global'
        # veryify exactly 2 arguments
        if len(Instruct.Arguments) != 2:
            print "Syntax error: MAKE/LOCALMAKE instructions must have 2 arguments in '%s'" % ErrProcName
            return False
        # check that the dest argument is a quoted word
        if Instruct.Arguments[0].ArgType != ParamType.QUOTEDWORD:
            print "Syntax error: First input to MAKE/LOCALMAKE instructions must be a quoted word in '%s'" % ErrProcName
            return False
        # if the variable already exists, then no problem
        varname = Instruct.Arguments[0].ElemText[0][1:]
        vartype = Instruct.Arguments[1].ArgType
        if len([var for var in VarList if var.Name.lower() == varname.lower()]) > 0:
            return True
        # otherwise, create a new variable and copy the type from the argument (which is probably ParamType.UNKNOWN but could be QUOTEDWORD or LISTNUM or LISTCODE)
        newvar = Variable(varname)
        if not newvar.SetType(vartype):
            print "Syntax error: An object of type '%s' cannot be assigned to variable '%s' in '%s'" % (ParamType.Names[vartype], varname, ErrProcName)
            return False
        print "created variable %s with type %i" % (varname, vartype)
        # add a reference to the new Variable to the VarList
        VarList.append(newvar)
        return True


# this function is executed when this script is run (not imported)
if __name__ == '__main__':
    # run the main function at the top of this source file
    main()


