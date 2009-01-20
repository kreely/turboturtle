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
        # check for instruction arguments using un-defined variables
        for instruct in self.MainInstructions:
            if not TT_App.RecurseInstruction(TT_App.CheckVariables, instruct, None, self.GlobalVariables, None):
                return
        for proc in self.Procedures:
            for instruct in proc.Instructions:
                if not TT_App.RecurseInstruction(TT_App.CheckVariables, instruct, proc.Name, self.GlobalVariables, proc.LocalVariables):
                    return
        # check all the user-defined Procedures to find those which return no value, and set their return type to NOTHING
        for proc in self.Procedures:
            bReturnsValue = False
            for instruct in proc.Instructions:
                if not TT_App.RecurseInstruction(TT_App.NoOutputInstruction, instruct):
                    bReturnsValue = True
                    break
            if not bReturnsValue:
                proc.ReturnType = ParamType.NOTHING
        # now, the main "fix-up" loop where we iteratively discover the types of all variables, procedure arguments, etc
        while True:
            # loop until we don't fix up anything else
            nFixups = 0
            for instruct in self.MainInstructions:
                newfix = self.FixupRecurse(instruct, None)
                if newfix == None:
                    return
                nFixups += newfix
            for proc in self.Procedures:
                for instruct in proc.Instructions:
                    newfix = self.FixupRecurse(instruct, proc)
                    if newfix == None:
                        return
                    nFixups += newfix
            if nFixups == 0:
                break
        # then verify that all data types and object pointers are filled in
            

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
            for elem in arg.Elements:
                if elem.Type == ElemType.FUNC_CALL:
                    if not TT_App.RecurseInstruction(pFunction, elem.pInstruct, *extraargs):
                        return False
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.Elements[0].pInstruct:
                    if not TT_App.RecurseInstruction(pFunction, instr, *extraargs):
                        return False
        return True
    # recursive instruction walking loop, for fixing up data types
    def FixupRecurse(self, pInstruct, pCodeProc):
        nFixups = 0
        # call the function to fixup a single instruction
        newfix = self.FixupInstruction(pInstruct, pCodeProc)
        if newfix == None:
            return None
        nFixups += newfix
        # recurse through other instructions
        for arg in pInstruct.Arguments:
            for elem in arg.Elements:
                if elem.Type == ElemType.FUNC_CALL:
                    newfix = self.FixupRecurse(elem.pInstruct, pCodeProc)
                    if newfix == None:
                        return None
                    nFixups += newfix
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.Elements[0].pInstruct:
                    newfix = self.FixupRecurse(instr, pCodeProc)
                    if newfix == None:
                        return None
                    nFixups += newfix
        return nFixups

    # debug function
    def InstructPrint(self, instruct, indent):
        print " " * indent + "Name: %s" % instruct.Name
        indent += 4
        for arg in instruct.Arguments:
            print " " * indent + "Arg: ",
            for elem in arg.Elements:
                print "<%s> " % elem.Text,
                if elem.Type == ElemType.FUNC_CALL:
                    self.InstructPrint(elem.pInstruct, indent + 4)
            print
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.Elements[0].pInstruct:
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
                codelisttext = " ".join([elem.Text for elem in arg.Elements])
                codelistelems = Parser.ParseStreamElements(codelisttext, ProcName)
                # pull instructions out of the element list
                instr_codelist = []
                while len(codelistelems) > 0:
                    instruction = Parser.GetSingleInstruction(codelistelems, ProcName, Procedures)
                    if instruction is None:
                        return False
                    instr_codelist.append(instruction)
                # store this list of instructions in this argument.  this removes the original element lists
                arg.Elements = [ Element(ElemType.CODE_LIST, codelisttext, instr_codelist) ]
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
        elif Instruct.Name.lower() == 'output' and (ProcName is None or LocalVariables is None):
            print "Syntax error: OUTPUT used outside of procedure definition"
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
            print "Syntax error: First input to MAKE/LOCALMAKE instructions must be a quoted word (the variable's name) in '%s'" % ErrProcName
            return False
        # if the variable already exists, then no problem
        varname = Instruct.Arguments[0].Elements[0].Text[1:]
        vartype = Instruct.Arguments[1].ArgType
        if len([var for var in VarList if var.Name.lower() == varname.lower()]) > 0:
            return True
        # otherwise, create a new variable and copy the type from the argument (which is probably ParamType.UNKNOWN but could be QUOTEDWORD or LISTNUM or LISTCODE)
        newvar = Variable(varname)
        if not newvar.SetType(vartype):
            print "Syntax error: An object of type '%s' cannot be assigned to variable '%s' in '%s'" % (ParamType.Names[vartype], varname, ErrProcName)
            return False
        # add a references to the new Variable to the VarList and the Instruction object
        VarList.append(newvar)
        Instruct.pMakeVar = newvar
        return True

    # Check an instruction for any arguments using values stored in variables
    # Make sure that the variable names are defined (ie, there is no missing MAKE/LOCALMAKE)
    # Add references to the Variable object into elements with type VAR_VALUE
    @staticmethod
    def CheckVariables(Instruct, ProcName, GlobalVariables, LocalVariables):
        ErrProcName = ProcName or 'global'
        for arg in Instruct.Arguments:
            for elem in arg.Elements:
                if elem.Type == ElemType.VAR_VALUE:
                    varname = elem.Text[1:]
                    if LocalVariables is not None:
                        localvars = [ var for var in LocalVariables if var.Name.lower() == varname.lower() ]
                        if len(localvars) > 0:
                            elem.pVariable = localvars[0]
                            continue
                    globalvars = [ var for var in GlobalVariables if var.Name.lower() == varname.lower() ]
                    if len(globalvars) > 0:
                        elem.pVariable = globalvars[0]
                        continue
                    print "Syntax error: variable '%s' in procedure '%s' is not defined (no MAKE instruction)" % (varname, ErrProcName)
                    return False
        return True

    # this is used to find any OUTPUT instructions in a procedure, which means that the procedure returns a value
    @staticmethod
    def NoOutputInstruction(Instruct):
        if Instruct.BuiltIn is True and Instruct.Name == 'output':
            return False
        return True

    # Basic instruction fix-up function; this gets called iteratively for each instruction in the tree until there are no more fixups
    def FixupInstruction(self, pInstruct, pCodeProc):
        if pCodeProc is not None:
            ErrProcName = pCodeProc.Name
        else:
            ErrProcName = 'global'
        nFixups = 0
        # start by discovering the ArgType for any arguments with an UNKNOWN type
        for arg in pInstruct.Arguments:
            if arg.ArgType == ParamType.UNKNOWN:
                # we must pass a copy of the list to the GetExpressionType function, because this list will be destroyed
                argtype = Argument.GetExpressionType(arg.Elements[:])
                if argtype is None:
                    return None
                if argtype == ParamType.NOTHING:
                    print "Logical error in procedure '%s': Procedure returning type NOTHING is not allowed in an expression" % ErrProcName
                    return None
                if argtype != ParamType.UNKNOWN:
                    arg.ArgType = argtype
                    nFixups += 1
        # next, try to discover exactly which procedure is being called by this instruction
        if pInstruct.pProc is None and len([arg for arg in pInstruct.Arguments if arg.ArgType == ParamType.UNKNOWN]) == 0:
            # look for built-in procedures
            if pInstruct.BuiltIn == True:
                for proc in Builtin._procs:
                    if pInstruct.Name.lower() != proc.FullName and pInstruct.Name.lower() != proc.AbbrevName:
                        continue
                    if pInstruct.bParenthesized != proc.bParenthesized:
                        continue
                    if not (pInstruct.nParams == proc.nParams or (pInstruct.bExtraArgs and proc.bExtraArgs and pInstruct.nParams > proc.nParams)):
                        continue
                    argsmatch = True
                    for i in range(proc.nParams):
                        if proc.ParamTypes[i] != ParamType.ANYTHING and pInstruct.Arguments[i].ArgType != proc.ParamTypes[i]:
                            argsmatch = False
                    if not argsmatch:
                        continue
                    # we found a match!
                    pInstruct.pProc = proc
                    nFixups += 1
                    break
            # then look at the user-defined procedures
            else:
                for proc in self.Procedures:
                    if pInstruct.Name.lower() != proc.Name.lower():
                        continue
                    # we found a match: forward param types from instructions to procedure inputs, and check existing types
                    for i in range(pInstruct.nParams):
                        if proc.InputVariables[i].Type == ParamType.UNKNOWN:
                            proc.InputVariables[i].Type = pInstruct.Arguments[i].ArgType
                            nFixups += 1
                            continue
                        if proc.InputVariables[i].Type != pInstruct.Arguments[i].ArgType:
                            print "Logical error: procedure '%s' expects input #%i to be type '%s', but is called with '%s'" % (proc.Name, i+1, ParamType.Names[proc.InputVariables[i].Type], ParamType.Names[pInstruct.Arguments[i].ArgType])
                            return None
                    pInstruct.pProc = proc
                    nFixups += 1
                    break
        # forward ParamTypes through MAKE/LOCALMAKE instructions
        if pInstruct.BuiltIn is True and pInstruct.pProc is not None and (pInstruct.pProc.FullName == 'make' or pInstruct.pProc.FullName == 'localmake'):
            argtype = pInstruct.Arguments[1].ArgType
            if argtype != ParamType.UNKNOWN:
                if pInstruct.pMakeVar.Type == ParamType.UNKNOWN:
                    pInstruct.pMakeVar.Type = argtype
                    nFixups += 1
                elif pInstruct.pMakeVar.Type != argtype:
                    print "Logical error: %s instruction setting variable already type '%s' with argument of type '%s'" % (pInstruct.Name, ParamType.Names[pInstruct.MakeVar.Type], ParamType.Names[argtype])
                    return None
        # forward ParamType from OUTPUT argument to procedure return type
        if pInstruct.BuiltIn is True and pInstruct.pProc is not None and pInstruct.pProc.FullName == 'output':
            argtype = pInstruct.Arguments[0].ArgType
            if argtype != ParamType.UNKNOWN:
                if pCodeProc.ReturnType == ParamType.UNKNOWN:
                    pCodeProc.ReturnType = argtype
                    nFixups += 1
                elif pCodeProc.ReturnType != argtype:
                    print "Logical error: Procedure '%s' OUTPUTs values of both type '%s' and type '%s'" % (pCodeProc.Name, ParamType.Names[pCodeProc.ReturnType], ParamType.Names[argtype])
                    return None
        # at the end, return the # of fixups that we did
        return nFixups

# this function is executed when this script is run (not imported)
if __name__ == '__main__':
    # run the main function at the top of this source file
    main()


