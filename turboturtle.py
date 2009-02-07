#!/usr/bin/env python
#==================================================
# TurboTurtle.py - 2009-01-13
# A Logo to C++ translator for fast Turtle Graphics
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

import os, sys
from tt_types import *
from tt_parser import *
from tt_builtin import *
from tt_variable import *
from tt_procedure import *
from tt_cppwriter import *
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
    if not app.Run():
        sys.exit(1)
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
            return False
        # the next step is to parse instructions for the main code and the subroutines
        self.MainInstructions = self.ParseInstructions(self.MainCode, None)
        if self.MainInstructions is None:
            return False
        for proc in self.Procedures:
            proc.Instructions = self.ParseInstructions(proc.CodeText, proc)
            if proc.Instructions is None:
                return False
        # create local/global variables from MAKE, LOCALMAKE, and FOR instructions
        self.GlobalVariables = []
        if not self.RecurseAllInstructions(self.CreateVarFromInstruct):
            return False
        # check for instruction arguments using un-defined variables
        if not self.RecurseAllInstructions(self.CheckVariables):
            return False
        # check all the user-defined Procedures to find those which return no value, and set their return type to NOTHING
        for proc in self.Procedures:
            bReturnsValue = False
            for instruct in proc.Instructions:
                if not self.RecurseInstruction(self.NoOutputInstruction, instruct, proc):
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
                    return False
                nFixups += newfix
            for proc in self.Procedures:
                for instruct in proc.Instructions:
                    newfix = self.FixupRecurse(instruct, proc)
                    if newfix == None:
                        return False
                    nFixups += newfix
            if nFixups == 0:
                break
        # look for unused procedures and remove them
        pUnusedProcs = self.Procedures[:]  # make a copy of the list so we dont trash self.Procedures
        if not self.RecurseAllInstructions(self.RemoveCalledProcedures, pUnusedProcs):
            return False
        for proc in pUnusedProcs:
            self.Procedures.remove(proc)
        # look for unused global variables and remove them as well (they may have been used only in a deleted procedure)
        pUnusedGlobals = self.GlobalVariables[:]  # make a copy of the list so we don't trash self.GlobalVariables
        if not self.RecurseAllInstructions(self.RemoveUsedGlobals, pUnusedGlobals):
            return False
        for var in pUnusedGlobals:
            self.GlobalVariables.remove(var)
        # verify that the ParamTypes of all global and local variables are defined
        for var in self.GlobalVariables:
            if var.Type == ParamType.UNKNOWN:
                print "Logical error: Type of global variable named '%s' cannot be determined." % var.Name
                return False
        for proc in self.Procedures:
            for var in proc.LocalVariables:
                if var.Type == ParamType.UNKNOWN:
                    print "Logical error: Type of local variable named '%s' in procedure '%s' cannot be determined." % (var.Name, proc.Name)
                    return False
        # verify that Return value for each Procedure is defined
        for proc in self.Procedures:
            if proc.ReturnType == ParamType.UNKNOWN:
                print "Logical error: Type of return value from procedure '%s' cannot be determined." % proc.Name
                return False
        # verify that the Procedure pointers and ParamType of all Arguments in each instruction are defined
        if not self.RecurseAllInstructions(self.FinalInstructionCheck):
            return False
        # at this point, the "front end" of the compiler is done and only the back-end work remains
        writer = CppWriter()
        # start by creating C++-friendly names for all of the procedures and variables
        for var in self.GlobalVariables:
            var.CppName = "g_%s" % CppWriter.GetValidCppName(var.Name)
        for proc in self.Procedures:
            proc.CppName = "_%s" % CppWriter.GetValidCppName(proc.Name)
            for var in proc.LocalVariables:
                var.CppName = "l_%s" % CppWriter.GetValidCppName(var.Name)
        # Initialize to default the state variables which have an impact on the resulting C++ code
        writer.InitDefaultState()
        # Then go through every instruction in the program and modify these state variables according to the Logo code
        if not self.RecurseAllInstructions(writer.SetStateFromInstruction):
            return False
        # Now start the output of C++ code by writing global variable definitions
        GlobalInitCode = writer.WriteGlobals(self.GlobalVariables)
        if GlobalInitCode is None:
            return False
        # Next, write the function definitions for the user-defined Logo procedures
        if len(self.Procedures) > 0:
            writer.OutputText += "// Function definitions for Logo procedures\n"
        for proc in self.Procedures:
            writer.OutputText += "static "
            if not writer.WriteFunctionPrototype(proc):
                return False
            writer.OutputText += ";\n"
        if len(self.Procedures) > 0:
            writer.OutputText += "\n"
        # write out the main function
        writer.OutputText += "void tt_LogoMain(void)\n{\n"
        if GlobalInitCode != "":
            writer.OutputText += " " * writer.IndentSize + "// initialize global variables\n"
            writer.OutputText += GlobalInitCode
        writer.InitProcedure()
        for instruct in self.MainInstructions:
            if not writer.WriteInstruction(instruct, 1, True):
                return False
        writer.OutputText += "}\n\n"
        # write out all the procedures
        for proc in self.Procedures:
            # start with the function definition and opening brace
            if not writer.WriteFunctionPrototype(proc):
                return False
            writer.OutputText += "\n{\n"
            # then definitions and initialization of local variables
            LocalInitCode = ""
            LocalVars = 0
            for var in proc.LocalVariables:
                if var in proc.InputVariables:
                    continue
                LocalVars += 1
                Code = writer.WriteVariableDefinition(var, 1)
                if Code is None:
                    return False
                LocalInitCode += Code
            if LocalVars > 0:
                writer.OutputText += "\n"
            if LocalInitCode != "":
                writer.OutputText += LocalInitCode + "\n"
            # lastly, write out all the instructions
            writer.InitProcedure()
            for instruct in proc.Instructions:
                if not writer.WriteInstruction(instruct, 1, True):
                    return False
            writer.OutputText += "}\n\n"
        # Compilation done!  Write the logo source code and save the output text into the destination file
        writer.OutputText += "/***** The LOGO source code from which this file was compiled is given here *****/\n"
        for line in InputCodeRaw.split('\n'):
            writer.OutputText += "// %s\n" % line
        f = open(self.OutputName, 'w')
        f.write(writer.OutputText)
        f.close()
        return True

    def DebugPrintCodeStructure(self):
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

    # call a function for all instructions in the world: both in the main function and in all the procedures
    def RecurseAllInstructions(self, pFunction, *extraargs):
        for instruct in self.MainInstructions:
            if not self.RecurseInstruction(pFunction, instruct, None, *extraargs):
                return False
        for proc in self.Procedures:
            for instruct in proc.Instructions:
                if not self.RecurseInstruction(pFunction, instruct, proc, *extraargs):
                    return False
        return True
    # instruction recursion loop, accepting a function to call for each instruction
    def RecurseInstruction(self, pFunction, instruct, pCodeProc, *extraargs):
        # call the given function
        if not pFunction(instruct, pCodeProc, *extraargs):
            return False
        # recurse through other instructions
        for arg in instruct.Arguments:
            for elem in arg.Elements:
                if elem.Type == ElemType.FUNC_CALL:
                    if not self.RecurseInstruction(pFunction, elem.pInstruct, pCodeProc, *extraargs):
                        return False
            if arg.ArgType == ParamType.LISTCODE:
                for instr in arg.Elements[0].pInstruct:
                    if not self.RecurseInstruction(pFunction, instr, pCodeProc, *extraargs):
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
    def ParseInstructions(self, CodeText, pCodeProc):
        if pCodeProc is None:
            ProcName = None
        else:
            ProcName = pCodeProc.Name
        # parse the instruction stream into a list of elements
        Elements = Parser.ParseStreamElements(CodeText, ProcName)
        if Elements is None:
            return None
        # pull instructions out of the element list
        Instructions = []
        while len(Elements) > 0:
            instruction = Parser.GetSingleInstruction(Elements, ProcName, self.Procedures)
            if instruction is None:
                return None
            # parse the Instruction lists in procedure arguments
            if not self.RecurseInstruction(self.ParseInstructionsInArgs, instruction, pCodeProc):
                return None
            # syntax error if a built-in instruction (outside of an expression) does not return NOTHING
            if instruction.bBuiltIn is True:
                InstructName = instruction.Name.lower()
                proclist = [ proc for proc in Builtin._procs if proc.FullName == InstructName or proc.AbbrevName == InstructName ]
                if proclist[0].ReturnType != ParamType.NOTHING:
                    print "Syntax error: return value of '%s' instruction is unused" % InstructName
                    return None
            Instructions.append(instruction)
        # for instr in Instructions:
        return Instructions
    def ParseInstructionsInArgs(self, Instruct, pCodeProc):
        if pCodeProc is None:
            ProcName = None
        else:
            ProcName = pCodeProc.Name
        for arg in Instruct.Arguments:
            if arg.ArgType == ParamType.LISTCODE:
                # convert the list (without brackets) back to text, and re-read the elements as a new instructions
                codelisttext = " ".join([elem.Text for elem in arg.Elements])
                codelistelems = Parser.ParseStreamElements(codelisttext, ProcName)
                # pull instructions out of the element list
                instr_codelist = []
                while len(codelistelems) > 0:
                    instruction = Parser.GetSingleInstruction(codelistelems, ProcName, self.Procedures)
                    if instruction is None:
                        return False
                    # syntax error if a built-in instruction (outside of an expression) does not return NOTHING
                    if instruction.bBuiltIn is True:
                        InstructName = instruction.Name.lower()
                        proclist = [ proc for proc in Builtin._procs if proc.FullName == InstructName or proc.AbbrevName == InstructName ]
                        if proclist[0].ReturnType != ParamType.NOTHING:
                            print "Syntax error: return value of '%s' instruction is unused" % InstructName
                            return False
                    instr_codelist.append(instruction)
                # store this list of instructions in this argument.  this removes the original element lists
                arg.Elements = [ Element(ElemType.CODE_LIST, codelisttext, instr_codelist) ]
        return True

    # functions to allocate a global or local variable from a MAKE, LOCALMAKE, or FOR procedure call
    # this also checks to make sure that an OUTPUT instruction is never called outside of a procedure
    def CreateVarFromInstruct(self, Instruct, pCodeProc):
        if Instruct.Name.lower() == 'for':
            if not self.CreateForLoopVar(Instruct, pCodeProc):
                return False
        elif Instruct.Name.lower() == 'make':
            if not self.CreateVar(Instruct, pCodeProc, self.GlobalVariables):
                return False
        elif Instruct.Name.lower() == 'localmake':
            if pCodeProc is None:
                print "Syntax error: LOCALMAKE used outside of procedure definition"
                return False
            if not self.CreateVar(Instruct, pCodeProc, pCodeProc.LocalVariables):
                return False
        elif Instruct.Name.lower() == 'output' and pCodeProc is None:
            print "Syntax error: OUTPUT used outside of procedure definition"
            return False
        return True
    def CreateVar(self, Instruct, pCodeProc, VarList):
        if pCodeProc is None:
            ErrProcName = 'global'
        else:
            ErrProcName = pCodeProc.Name
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
        foundvars = [var for var in VarList if var.Name.lower() == varname.lower()]
        if len(foundvars) > 0:
            Instruct.pMakeVar = foundvars[0]
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
    def CreateForLoopVar(self, Instruct, pCodeProc):
        if pCodeProc is None:
            ErrProcName = 'global'
        else:
            ErrProcName = pCodeProc.Name
        # check that the dest argument is a quoted word
        if Instruct.Arguments[0].ArgType != ParamType.QUOTEDWORD:
            print "Internal error: First input to FOR instruction must be a variable name in '%s'" % ErrProcName
            return False
        # set the varlist according to whether or not we are inside of a procedure definition
        if pCodeProc is None:
            varlist = self.GlobalVariables
        else:
            varlist = pCodeProc.LocalVariables
        # if the variable already exists, then check type to make sure it's not incompatible and return
        varname = Instruct.Arguments[0].Elements[0].Text[1:]
        foundvars = [var for var in varlist if var.Name.lower() == varname.lower()]
        if len(foundvars) > 0:
            Instruct.pMakeVar = foundvars[0]
            if foundvars[0].Type == ParamType.UNKNOWN:
                foundvars[0].Type = ParamType.NUMBER
            elif foundvars[0].Type != ParamType.NUMBER:
                print "Syntax error: Variable '%s' in FOR instruction in procedure '%s' must be a number, but its already type '%s'" % (varname, ErrProcName, ParamType.Names[foundvars[0].Type])
                return False
            return True
        # otherwise, create a new variable
        newvar = Variable(varname)
        newvar.SetType(ParamType.NUMBER)
        # add a references to the new Variable to the VarList and the Instruction object
        varlist.append(newvar)
        Instruct.pMakeVar = newvar
        return True

    # Check an instruction for any arguments using values stored in variables
    # Make sure that the variable names are defined (ie, there is no missing MAKE/LOCALMAKE)
    # Add references to the Variable object into elements with type VAR_VALUE
    # Check for MAKE instruction which writes to a global variable with the same name as a local variable
    def CheckVariables(self, Instruct, pCodeProc):
        if pCodeProc is None:
            ErrProcName = 'global'
        else:
            ErrProcName = pCodeProc.Name
        for arg in Instruct.Arguments:
            for elem in arg.Elements:
                if elem.Type == ElemType.VAR_VALUE:
                    varname = elem.Text[1:]
                    if pCodeProc is not None:
                        localvars = [ var for var in pCodeProc.LocalVariables if var.Name.lower() == varname.lower() ]
                        if len(localvars) > 0:
                            elem.pVariable = localvars[0]
                            continue
                    globalvars = [ var for var in self.GlobalVariables if var.Name.lower() == varname.lower() ]
                    if len(globalvars) > 0:
                        elem.pVariable = globalvars[0]
                        continue
                    print "Syntax error: variable '%s' in procedure '%s' is not defined (no MAKE instruction)" % (varname, ErrProcName)
                    return False
        if pCodeProc is not None and Instruct.Name.lower() == "make":
            localvars = [ var for var in pCodeProc.LocalVariables if var.Name.lower() == Instruct.pMakeVar.Name.lower() ]
            if len(localvars) > 0:
              print "Logical error: MAKE instruction for variable '%s' in procedure '%s' writes to global, but there is a local variable with the same name" % (Instruct.pMakeVar.Name.lower(), ErrProcName)
              return False
        return True

    # this is used to find any OUTPUT instructions in a procedure, which means that the procedure returns a value
    def NoOutputInstruction(self, Instruct, pCodeProc):
        if Instruct.bBuiltIn is True and Instruct.Name.lower() == 'output':
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
        unknownargs = len([arg for arg in pInstruct.Arguments if arg.ArgType == ParamType.UNKNOWN])
        for arg in pInstruct.Arguments:
            if arg.ArgType == ParamType.ARRAY and arg.Elements[0].Type == ElemType.VAR_VALUE:
                if arg.Elements[0].pVariable.ArrayDim is None:
                    unknownargs += 1
        if pInstruct.pProc is None and unknownargs == 0:
            # look for built-in procedures
            if pInstruct.bBuiltIn == True:
                for proc in Builtin._procs:
                    if pInstruct.Name.lower() != proc.FullName and pInstruct.Name.lower() != proc.AbbrevName:
                        continue
                    if proc.bParenthesized and not pInstruct.bParenthesized:
                        continue
                    if not (pInstruct.nParams == proc.nParams or (pInstruct.bExtraArgs and proc.bExtraArgs and pInstruct.nParams > proc.nParams)):
                        continue
                    argsmatch = True
                    for i in range(proc.nParams):
                        if proc.ParamTypes[i] != ParamType.ANYTHING and pInstruct.Arguments[i].ArgType != proc.ParamTypes[i]:
                            argsmatch = False
                    if not argsmatch:
                        continue
                    # if this is a parenthesized, extra-argument instruction, make sure that all extra args have the same type as the last arg
                    if proc.bParenthesized and proc.bExtraArgs:
                        lastargtype = proc.ParamTypes[proc.nParams-1]
                        for i in range(proc.nParams, pInstruct.nParams):
                            if pInstruct.Arguments[i].ArgType != lastargtype and lastargtype != ParamType.ANYTHING:
                                print "Syntax error: parenthesized instruction '%s' requires all extra arguments to be type '%s'" % (pInstruct.Name, ParamType.Names[lastargtype])
                                return None
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
                        elif proc.InputVariables[i].Type != pInstruct.Arguments[i].ArgType:
                            print "Logical error: procedure '%s' expects input #%i to be type '%s', but is called with '%s'" % (proc.Name, i+1, ParamType.Names[proc.InputVariables[i].Type], ParamType.Names[pInstruct.Arguments[i].ArgType])
                            return None
                        if proc.InputVariables[i].Type == ParamType.ARRAY:
                            if proc.InputVariables[i].ArrayDim is None:
                                proc.InputVariables[i].ArrayDim = pInstruct.Arguments[i].Elements[0].pVariable.ArrayDim
                                nFixups += 1
                            elif proc.InputVariables[i].ArrayDim != pInstruct.Arguments[i].Elements[0].pVariable.ArrayDim:
                                print "Logical error: procedure '%s' expects input #%i to be an array with dimension %i, but is called with an array dimension %i" % (proc.Name, i+1, proc.InputVariables[i].ArrayDim, pInstruct.Arguments[i].Elements[0].pVariable.ArrayDim)
                                return None
                    pInstruct.pProc = proc
                    nFixups += 1
                    break
        # Set dimensions of array returned from ARRAY, MDARRAY instructions
        if pInstruct.bBuiltIn is True and pInstruct.pProc is not None and pInstruct.pProc.FullName in ('array', 'mdarray'):
            if pInstruct.pProc.FullName == 'array' and pInstruct.ReturnArrayDim == None:
                pInstruct.ReturnArrayDim = 1
                nFixups += 1
            elif pInstruct.pProc.FullName == 'mdarray' and pInstruct.ReturnArrayDim == None:
                if pInstruct.Arguments[0].Elements[0].Type == ElemType.NUMBER:
                    pInstruct.ReturnArrayDim = len(pInstruct.Arguments[0].Elements)
                    nFixups += 1
                elif pInstruct.Arguments[0].Elements[0].Type == ElemType.FUNC_CALL:
                    if pInstruct.Arguments[0].Elements[0].Text.lower() != "list":
                        print "Syntax error: invalid function call '%s' in first parameter to MDARRAY instruction. Only LIST is allowed." % pInstruct.Arguments[0].Elements[0].Text
                        return None
                    pInstruct.ReturnArrayDim = len(pInstruct.Arguments[0].Elements[0].pInstruct.Arguments)
                    nFixups += 1
                else:
                    print "Syntax error: Invalid parameter '%s' to MDARRAY instruction. Only a list of numbers or a LIST instruction is allowed." % pInstruct.Arguments[0].Elements[0].Text
                    return None
        # forward ParamTypes through MAKE/LOCALMAKE instructions
        if pInstruct.bBuiltIn is True and pInstruct.pProc is not None and pInstruct.pProc.FullName in ('make', 'localmake'):
            argtype = pInstruct.Arguments[1].ArgType
            if argtype != ParamType.UNKNOWN:
                if pInstruct.pMakeVar.Type == ParamType.UNKNOWN:
                    pInstruct.pMakeVar.Type = argtype
                    nFixups += 1
                elif pInstruct.pMakeVar.Type != argtype:
                    print "Logical error: %s instruction setting variable already type '%s' with argument of type '%s'" % (pInstruct.Name, ParamType.Names[pInstruct.pMakeVar.Type], ParamType.Names[argtype])
                    return None
            # set array dimensions for destination variable of MAKE/LOCALMAKE
            if argtype == ParamType.ARRAY and pInstruct.pMakeVar.ArrayDim is None:
                elem0 = pInstruct.Arguments[1].Elements[0]
                if elem0.Type == ElemType.VAR_VALUE and elem0.pVariable.ArrayDim is not None:
                    pInstruct.pMakeVar.ArrayDim = elem0.pVariable.ArrayDim
                    nFixups += 1
                elif elem0.Type == ElemType.FUNC_CALL and elem0.pInstruct.ReturnArrayDim is not None:
                    pInstruct.pMakeVar.ArrayDim = elem0.pInstruct.ReturnArrayDim
                    nFixups += 1
        # forward ParamType from OUTPUT argument to procedure return type
        if pInstruct.bBuiltIn is True and pInstruct.pProc is not None and pInstruct.pProc.FullName == 'output':
            argtype = pInstruct.Arguments[0].ArgType
            if argtype == ParamType.ARRAY:
                print "Logical error: OUTPUT instruction cannot return an ARRAY in procedure '%s'" % pCodeProc.Name
                return None
            elif argtype != ParamType.UNKNOWN:
                if pCodeProc.ReturnType == ParamType.UNKNOWN:
                    pCodeProc.ReturnType = argtype
                    nFixups += 1
                elif pCodeProc.ReturnType != argtype:
                    print "Logical error: Procedure '%s' OUTPUTs values of both type '%s' and type '%s'" % (pCodeProc.Name, ParamType.Names[pCodeProc.ReturnType], ParamType.Names[argtype])
                    return None
        # at the end, return the # of fixups that we did
        return nFixups

    # Examine an instruction, and if it calls a procedure in the Unused list, remove that procedure from the Unused list
    # Note: procedures calling themselves don't count
    def RemoveCalledProcedures(self, pInstruct, pCodeProc, pUnusedProcs):
        if pInstruct.pProc is not None and pInstruct.pProc in pUnusedProcs and pInstruct.pProc != pCodeProc:
            pUnusedProcs.remove(pInstruct.pProc)
        return True

    # Examine an instruction, and if it makes or uses a global variable in the Unused list, remove that variable from the list
    def RemoveUsedGlobals(self, pInstruct, pCodeProc, pUnusedGlobals):
        # first, check the Instruction's pMakeVar to see if this global is written
        if pInstruct.pMakeVar is not None and pInstruct.pMakeVar in pUnusedGlobals:
            pUnusedGlobals.remove(pInstruct.pMakeVar)
        # then check all the argument elements for a reference to this variable
        for arg in pInstruct.Arguments:
            for elem in arg.Elements:
                if elem.Type == ElemType.VAR_VALUE and elem.pVariable is not None and elem.pVariable in pUnusedGlobals:
                    pUnusedGlobals.remove(elem.pVariable)
        return True

    # verify that the Procedure pointer and ParamType of all Arguments in an instruction are defined
    def FinalInstructionCheck(self, pInstruct, pCodeProc):
        if pInstruct.pProc is None:
            print "Logical error: couldn't find matching procedure '%s'.  Probably the given argument Types (%s) don't match the Procedure input Types." % (pInstruct.Name, ",".join([ParamType.Names[arg.ArgType] for arg in pInstruct.Arguments]))
            return False
        for i in range(len(pInstruct.Arguments)):
            if pInstruct.Arguments[i].ArgType == ParamType.UNKNOWN:
                # this should never happen, because the fixup loop won't set the pProc pointer if there are any UNKNOWN argument types
                print "Internal error: couldn't determine Type for argument #%i in '%s' procedure call" % (i+1, pInstruct.Name)
                return False
        return True

# this function is executed when this script is run (not imported)
if __name__ == '__main__':
    # run the main function at the top of this source file
    main()


