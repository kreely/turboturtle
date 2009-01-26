#==================================================
# tt_cppwriter.py - 2009-01-22
# Back-end functions for Turbo Turtle (writing the CPP file)
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *
from tt_variable import *
from tt_procedure import *
from tt_instruction import *

# CPP Output file header
CppHead = """
/********************************************/
/* Turbo Turtle Logo Compiled C++ Core File */
/*                                          */
/* This code is automatically generated     */
/********************************************/

#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <SDL_opengl.h>
#include "wrapper_api.h"

"""

class CppWriter():
    def __init__(self):
        # Parameters of cppwriter
        self.IndentSize = 4
        # global variables
        self.LogoState = Struct()
        self.OutputText = CppHead

#------------------------------------------------------------------------
# Functions called by turboturtle.py
#------------------------------------------------------------------------

    # this function replaces invalid chars in Logo names with underscores to make a valid C++ name
    @staticmethod
    def GetValidCppName(LogoName):
        CppName = ""
        for ch in LogoName:
            if ch in '0123456789_' or (ch.lower() >= 'a' and ch.lower() <= 'z'):
                CppName += ch
            else:
                CppName += '_'
        return CppName

    # Initialize the default 'static' state of the compiled Logo code
    def InitDefaultState(self):
        self.LogoState.iWindowSize = 100
        self.LogoState.bUseScrunch = False
        self.LogoState.bUseWrap = False
        self.LogoState.bNeedColors = False
        self.LogoState.NumType = 'float'
        self.LogoState.TempIdx = 0
        self.LogoState.LoopIdx = 0          # each REPEAT or FOREVER instruction gets its own local counter variable
        self.LogoState.InnerLoopIdx = -1    # this is the index of the loop counter for the current innermost loop, for handling REPCOUNT

    # parse each instruction in the program and modify our LogoState accordingly
    def SetStateFromInstruction(self, pInstruct, pCodeProc):
        if pInstruct.Name.lower() == '.setspecial':
            if len(pInstruct.Arguments[1].Elements) != 1 or pInstruct.Arguments[1].Elements[0].Type != ElemType.NUMBER:
                print "Syntax error: invalid use of .setspecial: only immediate numeric values are allowed"
                return False
            specialname = pInstruct.Arguments[0].Elements[0].Text[1:].lower()
            specialnum = float(pInstruct.Arguments[1].Elements[0].Text)
            if specialname == 'windowsize':
                self.LogoState.iWindowSize = int(specialnum)
            elif specialname == 'highprecision':
                if int(specialnum) != 0:
                    self.LogoState.NumType = 'double'
            else:
                print "Warning: .setspecial instruction used with unknown variable '%s'" % specialname
        elif pInstruct.Name.lower() in ('setpencolor', 'setpc', 'setbackground', 'setbg') and pInstruct.Arguments[0].ArgType == ParamType.NUMBER:
            self.LogoState.bNeedColors = True
        elif pInstruct.Name.lower() == 'setscrunch':
            self.LogoState.bUseScrunch = True
        elif pInstruct.Name.lower() in ('wrap', 'window'):
            self.LogoState.bUseWrap = True
        return True

    # Write out the global variables for the CPP code
    def WriteGlobals(self, GlobalVariables):
        # start by writing the special TurboTurtle variables
        self.OutputText += "static const %s tt_DegreeRad = 180.0 / 3.141592653589793;\n" % self.LogoState.NumType
        self.OutputText += "static const %s tt_RadDegree = 3.141592653589793 / 180.0;\n" % self.LogoState.NumType
        self.OutputText += "%s tt_TurtlePos[2] = {0.0, 0.0};\n" % self.LogoState.NumType
        self.OutputText += "%s tt_TurtleDir = 0.0;\n" % self.LogoState.NumType
        self.OutputText += "%s tt_NewPos[2] = {0.0, 0.0};\n" % self.LogoState.NumType
        self.OutputText += "bool tt_PenDown = true;\n"
        if self.LogoState.bNeedColors:
            self.OutputText += "unsigned char tt_Colors[16][4] = {{0,0,0,0}, {0,0,255,0}, {0,255,0,0}, {0,255,255,0}, {255,0,0,0}, {255,0,255,0}, {255,255,0,0}, {255,255,255,0}, {160,82,45,0}, {210,180,140,0}, {34,139,34,0}, {127,255,212,0}, {250,128,114,0}, {128,0,128,0}, {255,165,0,0}, {128,128,128,0}};\n"
        if self.LogoState.bUseScrunch:
            self.OutputText += "%s tt_ScrunchXY[2] = {1.0, 1.0};\n" % self.LogoState.NumType
        if self.LogoState.bUseWrap:
            self.OutputText += "bool tt_UseWrap = false;\n"
        # then write out C++ definitions for the Logo program's global variables
        self.OutputText += "\n"
        InitCode = ""
        for var in GlobalVariables:
            Code = self.WriteVariableDefinition(var, 0)
            if Code is None:
                return None
            InitCode += Code
        if len(GlobalVariables) > 0:
            self.OutputText += "\n"
        return InitCode

    # Write out a function prototypes
    def WriteFunctionPrototype(self, pProc):
        # start with the return type
        if not self.WriteVarType(pProc.ReturnType):
            return False
        # then the name
        self.OutputText += " " + pProc.CppName + "("
        # lastly, the input arguments
        bFirst = True
        for var in pProc.InputVariables:
            if not bFirst:
                self.OutputText += ", "
            else:
                bFirst = False
            if not self.WriteVarType(var.Type):
                return False
            self.OutputText += " " + var.CppName
        self.OutputText += ")"
        return True

    # Write out variable definition
    def WriteVariableDefinition(self, Var, iIndent):
        InitCode = ""
        # write leading white space, the variable's C++ type, and name
        self.OutputText += " " * (iIndent * self.IndentSize)
        if not self.WriteVarType(Var.Type):
            return None
        self.OutputText += " " + Var.CppName
        # next write initialization code
        if Var.Type == ParamType.BOOLEAN:
            self.OutputText += " = false;\n"
        elif Var.Type == ParamType.NUMBER:
            self.OutputText += " = 0.0;\n"
        elif Var.Type == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return None
        elif Var.Type == ParamType.ARRAY:
            print "Internal error: Arrays not yet supported."
            return None
        elif Var.Type == ParamType.QUOTEDWORD:
            self.OutputText += ' = "";\n'
        else:
            print "Internal error: invalid variable type %i in WriteVarType()" % Var.Type
            return None
        return InitCode

    # Set up the CppWriter object to get ready to output Instructions for a function (either main or a user-defined procedure)
    def InitProcedure(self):
        self.LogoState.TempIdx = 0
        self.LogoState.LoopIdx = 0
        self.LogoState.InnerLoopIdx = -1

    # Write out a single instruction (recursively)
    def WriteInstruction(self, pInstruct, iIndent, bTerminateLine):
        if pInstruct.bBuiltIn is True:
            return self.WriteBuiltInInstruction(pInstruct, iIndent)
        else:
            if not self.WriteUserInstruction(pInstruct, iIndent):
                return False
            if bTerminateLine is True:
                self.OutputText += ";\n"
            return True
            

#------------------------------------------------------------------------
# Functions only for internal use by tt_cppwriter.py
#------------------------------------------------------------------------

    def WriteVarType(self, Type):
        if Type == ParamType.NOTHING:
            self.OutputText += "void"
            return True
        elif Type == ParamType.BOOLEAN:
            self.OutputText += "bool"
            return True
        elif Type == ParamType.NUMBER:
            self.OutputText += self.LogoState.NumType
            return True
        elif Type == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return False
        elif Type == ParamType.ARRAY:
            print "Internal error: Arrays not yet supported."
            return False
        elif Type == ParamType.QUOTEDWORD:
            self.OutputText += "const char *"
            return True
        print "Internal error: invalid variable type %i in WriteVarType()" % Type
        return False

    def WriteArgument(self, Arg):
        if Arg.ArgType == ParamType.QUOTEDWORD:
            self.OutputText += '"' + Arg.Elements[0].Text[1:] + '"'
        elif Arg.ArgType == ParamType.ARRAY:
            print "Internal error: Arrays not yet supported."
            return False
        elif Arg.ArgType == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return False
        elif Arg.ArgType in (ParamType.NUMBER, ParamType.BOOLEAN):
            lastelem = None
            for elem in Arg.Elements:
                if elem.Type in (ElemType.OPEN_PAREN, ElemType.CLOSE_PAREN, ElemType.NUMBER, ElemType.BOOLEAN):
                    self.OutputText += elem.Text
                elif elem.Type == ElemType.INFIX_BOOL:
                    if elem.Text in ("<", ">", "<=", ">="):
                        self.OutputText += " " + elem.Text + " "
                    elif elem.Text == "=":
                        self.OutputText += " == "
                    elif elem.Text == "<>":
                        self.OutputText += " != "
                    else:
                        print "Internal error: invalid INFIX_BOOL element '%s' in WriteArgument()" % elem.Text
                        return False
                elif elem.Type == ElemType.INFIX_NUM:
                    if lastelem is not None and lastelem.Type == ElemType.INFIX_NUM and elem.Text == '-':
                        self.OutputText += "-"  # negative sign, don't include any spaces
                    else:
                        self.OutputText += " " + elem.Text + " "
                elif elem.Type == ElemType.VAR_VALUE:
                    self.OutputText += elem.pVariable.CppName
                elif elem.Type == ElemType.FUNC_CALL:
                    # recursively write a function call inside of a numeric/boolean expression
                    if not self.WriteInstruction(elem.pInstruct, 0, False):
                        return False
                else:
                    print "Internal error: invalid element type %i '%s' in WriteArgument()" % (elem.Type, elem.Text)
                    return False
                lastelem = elem
        else:
            print "Internal error: invalid argument type %i in WriteArgument()" % Arg.ArgType
            return False
        return True

    def WriteUserInstruction(self, pInstruct, iIndent):
        self.OutputText += " " * (iIndent * self.IndentSize)
        self.OutputText += pInstruct.pProc.CppName + "("
        bFirst = True
        for arg in pInstruct.Arguments:
            if bFirst is True:
                bFirst = False
            else:
                self.OutputText += ", "
            if not self.WriteArgument(arg):
                return None
        self.OutputText += ")"
        return True

    def WriteBuiltInInstruction(self, pInstruct, iIndent):
        IndentText = " " * (iIndent * self.IndentSize)
        if pInstruct.pProc.FullName == ".setspecial":                       # .SETSPECIAL
            return True
        elif pInstruct.pProc.FullName == "back":                            # BACK
            if not self.WriteBuiltinMove(IndentText, pInstruct.Arguments[0], "-"):
                return False
        elif pInstruct.pProc.FullName == "clean":                           # CLEAN
            self.OutputText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "clearscreen":                     # CLEARSCREEN
            # just move to HOME position and call clean
            self.OutputText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = tt_TurtleDir = 0.0;\n"
            self.OutputText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "for":                             # FOR
            my_temp = self.LogoState.TempIdx
            self.LogoState.TempIdx += 1
            varname = pInstruct.pMakeVar.CppName
            # write code to set the start value for the FOR loop
            self.OutputText += IndentText + "%s start%02i = " % (self.LogoState.NumType, my_temp)
            if not self.WriteArgument(pInstruct.Arguments[1]):
                return False
            self.OutputText += ";\n"
            # write code to set the limit value for the FOR loop
            self.OutputText += IndentText + "%s limit%02i = " % (self.LogoState.NumType, my_temp)
            if not self.WriteArgument(pInstruct.Arguments[2]):
                return False
            self.OutputText += ";\n"
            # write code to set the step size
            if pInstruct.Arguments[3].ArgType == ParamType.NUMBER:
                CodeList = pInstruct.Arguments[4].Elements[0].pInstruct
                self.OutputText += IndentText + "%s step%02i = " % (self.LogoState.NumType, my_temp)
                if not self.WriteArgument(pInstruct.Arguments[3]):
                    return False
                self.OutputText += ";\n"
            else:
                CodeList = pInstruct.Arguments[3].Elements[0].pInstruct
                self.OutputText += IndentText + "%s step%02i = start%02i <= limit%02i ? 1.0 : -1.0;\n" % (self.LogoState.NumType, my_temp, my_temp, my_temp)
            # now write the FOR loop
            self.OutputText += IndentText + "for (%s = start%02i; (%s - limit%02i) * step%02i <= 0.0; %s += step%02i)\n" % (varname, my_temp, varname, my_temp, my_temp, varname, my_temp)
            self.OutputText += IndentText + "{\n"
            for instruct in CodeList:
                if not self.WriteInstruction(instruct, iIndent + 1, True):
                    return False
            self.OutputText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "forever":                         # FOREVER
            my_counter = self.LogoState.LoopIdx
            self.LogoState.LoopIdx += 1
            self.OutputText += IndentText + "for (int loop%02i=1; ; loop%02i++)\n%s{\n" % (my_counter, my_counter, IndentText)
            for instruct in pInstruct.Arguments[0].Elements[0].pInstruct:
                self.LogoState.InnerLoopIdx = my_counter
                if not self.WriteInstruction(instruct, iIndent + 1, True):
                    return False
            self.OutputText += IndentText + "}\n"
            self.LogoState.InnerLoopIdx = -1
        elif pInstruct.pProc.FullName == "forward":                         # FORWARD
            if not self.WriteBuiltinMove(IndentText, pInstruct.Arguments[0], "+"):
                return False
        elif pInstruct.pProc.FullName == "home":                            # HOME
            self.OutputText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = tt_TurtleDir = 0.0;\n"
        elif pInstruct.pProc.FullName == "left":                            # LEFT
            if not self.WriteBuiltinTurn(IndentText, pInstruct.Arguments[0], "-"):
                return False
        elif pInstruct.pProc.FullName in ("localmake", "make"):             # LOCALMAKE, MAKE
            self.OutputText += IndentText + pInstruct.pMakeVar.CppName + " = "
            if not self.WriteArgument(pInstruct.Arguments[1]):
                return False
            self.OutputText += ";\n"
        elif pInstruct.pProc.FullName == "output":                          # OUTPUT
            self.OutputText += IndentText + "return "
            if not self.WriteArgument(pInstruct.Arguments[0]):
                return False
            self.OutputText += ";\n"
        elif pInstruct.pProc.FullName == "penup":                           # PENUP
            self.OutputText += IndentText + "tt_PenDown = false;\n"
        elif pInstruct.pProc.FullName == "pendown":                         # PENDOWN
            self.OutputText += IndentText + "tt_PenDown = true;\n"
        elif pInstruct.pProc.FullName == "penerase":                        # PENERASE
            self.OutputText += IndentText + "wrapper_SetPenPaint(false);\n"
        elif pInstruct.pProc.FullName == "penpaint":                        # PENPAINT
            self.OutputText += IndentText + "wrapper_SetPenPaint(true);\n"
        elif pInstruct.pProc.FullName == "repcount":                        # REPCOUNT
            if self.LogoState.InnerLoopIdx == -1:
                print "Syntax error: REPCOUNT instruction used outside of a FOREVER or REPEAT loop"
                return False
            self.OutputText += "loop%02i" % self.LogoState.InnerLoopIdx
        elif pInstruct.pProc.FullName == "repeat":                          # REPEAT
            my_counter = self.LogoState.LoopIdx
            self.LogoState.LoopIdx += 1
            self.OutputText += IndentText + "for (int loop%02i=1; loop%02i <= " % (my_counter, my_counter)
            if not self.WriteArgument(pInstruct.Arguments[0]):
                return False
            self.OutputText += "; loop%02i++)\n%s{\n" % (my_counter, IndentText)
            for instruct in pInstruct.Arguments[1].Elements[0].pInstruct:
                self.LogoState.InnerLoopIdx = my_counter
                if not self.WriteInstruction(instruct, iIndent + 1, True):
                    return False
            self.OutputText += IndentText + "}\n"
            self.LogoState.InnerLoopIdx = -1
        elif pInstruct.pProc.FullName == "right":                           # RIGHT
            if not self.WriteBuiltinTurn(IndentText, pInstruct.Arguments[0], "+"):
                return False
        elif pInstruct.pProc.FullName == "setbackground":                   # SETBACKGROUND
            if not self.WriteBuiltinSetColor(IndentText, pInstruct.Arguments[0], "wrapper_SetBackground"):
                return False
        elif pInstruct.pProc.FullName == "setpencolor":                     # SETPENCOLOR
            if not self.WriteBuiltinSetColor(IndentText, pInstruct.Arguments[0], "wrapper_SetPenColor"):
                return False
        elif pInstruct.pProc.FullName == "setpensize":                      # SETPENSIZE
            self.OutputText += IndentText + "wrapper_SetPenSize("
            if not self.WriteArgument(pInstruct.Arguments[0]):
                return False
            self.OutputText += ");\n"
        elif pInstruct.pProc.FullName == "setscrunch":                      # SETSCRUNCH
            self.OutputText += IndentText + "tt_ScrunchXY[0] = "
            if not self.WriteArgument(pInstruct.Arguments[0]):
                return False
            self.OutputText += ";\n"
            self.OutputText += IndentText + "tt_ScrunchXY[1] = "
            if not self.WriteArgument(pInstruct.Arguments[1]):
                return False
            self.OutputText += ";\n"
        elif pInstruct.pProc.FullName == "stop":                            # STOP
            self.OutputText += IndentText + "return;\n"
        elif pInstruct.pProc.FullName == "window":                          # WINDOW
            self.OutputText += IndentText + "tt_UseWrap = false;\n"
        elif pInstruct.pProc.FullName == "wrap":                            # WRAP
            self.OutputText += IndentText + "tt_UseWrap = true;\n"
        else:
            print "Internal error: built-in instruction named '%s' is not implemented" % pInstruct.Name
            return False
        return True

    def WriteBuiltinSetColor(self, IndentText, Arg, CoreFunc):
        if Arg.ArgType == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return False
        else: # must be ParamType.NUMBER
            nParen = 0
            if len(Arg.Elements) > 1:
                nParen = 1
            my_temp = self.LogoState.TempIdx
            self.LogoState.TempIdx += 1
            self.OutputText += IndentText + "int color%02i = (int) " % my_temp + "(" * nParen
            if not self.WriteArgument(Arg):
                return False
            self.OutputText += ")" * nParen + " & 15;\n"
            self.OutputText += IndentText + "%s(tt_Colors[color%02i][0], tt_Colors[color%02i][1], tt_Colors[color%02i][2]);\n" % (CoreFunc, my_temp, my_temp, my_temp)
        return True

    def WriteBuiltinTurn(self, IndentText, Arg, Sign):
        nParen = 0
        if len(Arg.Elements) > 1:
            nParen = 1
        self.OutputText += IndentText + "tt_TurtleDir " + Sign + "= " + "(" * nParen
        if not self.WriteArgument(Arg):
            return False
        self.OutputText += ")" * nParen + " * tt_RadDegree;\n"
        return True

    def WriteBuiltinMove(self, IndentText, Arg, DirSign):
        NextIndent = IndentText + " " * self.IndentSize
        ScrunchText = ""
        nParen = 0
        if len(Arg.Elements) > 1:
            nParen = 1
        # write code to calculate the new X position
        if self.LogoState.bUseScrunch:
            ScrunchText = " * tt_ScrunchXY[0]"
        self.OutputText += IndentText + "tt_NewPos[0] = tt_TurtlePos[0] %s cos(tt_TurtleDir) * %s" % (DirSign, "(" * nParen)
        if not self.WriteArgument(Arg):
            return False
        self.OutputText += ")" * nParen + ScrunchText + ";\n"
        # write code to calculate the new Y position
        if self.LogoState.bUseScrunch:
            ScrunchText = " * tt_ScrunchXY[1]"
        self.OutputText += IndentText + "tt_NewPos[1] = tt_TurtlePos[1] %s sin(tt_TurtleDir) * %s" % (DirSign, "(" * nParen)
        if not self.WriteArgument(Arg):
            return False
        self.OutputText += ")" * nParen + ScrunchText + ";\n"
        # write code to draw the line
        if self.LogoState.bUseWrap:
            self.OutputText += IndentText + "if (tt_PenDown)\n" + NextIndent + "wrapper_DrawLineSegment(tt_TurtlePos, tt_NewPos, tt_UseWrap);\n"
        else:
            self.OutputText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n" + NextIndent
            if self.LogoState.NumType == 'float':
                self.OutputText += "glVertex2f(tt_TurtlePos[0], tt_TurtlePos[1]);\n" + NextIndent
                self.OutputText += "glVertex2f(tt_NewPos[0], tt_NewPos[1]);\n" + IndentText + "}\n"
            else:
                self.OutputText += "glVertex2d(tt_TurtlePos[0], tt_TurtlePos[1]);\n" + NextIndent
                self.OutputText += "glVertex2d(tt_NewPos[0], tt_NewPos[1]);\n" + IndentText + "}\n"
        # write code to set the current position to the new position
        self.OutputText += IndentText + "tt_TurtlePos[0] = tt_NewPos[0];\n" + IndentText + "tt_TurtlePos[1] = tt_NewPos[1];\n"
        return True


