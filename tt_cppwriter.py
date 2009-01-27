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
        self.OutputText += "bool tt_PenDown = true;\n"
        self.OutputText += "bool tt_PenPaint = true;\n"
        self.OutputText += "int tt_WindowSize = %i;\n" % self.LogoState.iWindowSize
        self.OutputText += "unsigned char tt_ColorPen[4] = {255,255,255,0};\n"
        self.OutputText += "unsigned char tt_ColorBackground[4] = {0,0,0,0};\n"
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
        text = self.GetCppInstruction(pInstruct, iIndent, bTerminateLine)
        if text is None:
            return False
        self.OutputText += text
        return True

    def GetCppInstruction(self, pInstruct, iIndent, bTerminateLine):
        if pInstruct.bBuiltIn is True:
            return self.GetCppBuiltInInstruction(pInstruct, iIndent)
        else:
            text = self.GetCppUserInstruction(pInstruct, iIndent)
            if text is None:
                return False
            if bTerminateLine is True:
                text += ";\n"
            return text

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
        text = self.GetCppArgument(Arg)
        if text is None:
            return False
        self.OutputText += text
        return True

    def GetCppArgument(self, Arg):
        if Arg.ArgType == ParamType.QUOTEDWORD:
            return '"' + Arg.Elements[0].Text[1:] + '"'
        elif Arg.ArgType == ParamType.ARRAY:
            print "Internal error: Arrays not yet supported."
            return None
        elif Arg.ArgType == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return None
        elif Arg.ArgType in (ParamType.NUMBER, ParamType.BOOLEAN):
            lastelem = None
            CppText = ""
            for elem in Arg.Elements:
                if elem.Type in (ElemType.OPEN_PAREN, ElemType.CLOSE_PAREN, ElemType.NUMBER, ElemType.BOOLEAN):
                    CppText += elem.Text
                elif elem.Type == ElemType.INFIX_BOOL:
                    if elem.Text in ("<", ">", "<=", ">="):
                        CppText += " " + elem.Text + " "
                    elif elem.Text == "=":
                        CppText += " == "
                    elif elem.Text == "<>":
                        CppText += " != "
                    else:
                        print "Internal error: invalid INFIX_BOOL element '%s' in WriteArgument()" % elem.Text
                        return None
                elif elem.Type == ElemType.INFIX_NUM:
                    if lastelem is not None and lastelem.Type == ElemType.INFIX_NUM and elem.Text == '-':
                        CppText += "-"  # negative sign, don't include any spaces
                    else:
                        CppText += " " + elem.Text + " "
                elif elem.Type == ElemType.VAR_VALUE:
                    CppText += elem.pVariable.CppName
                elif elem.Type == ElemType.FUNC_CALL:
                    # recursively write a function call inside of a numeric/boolean expression
                    codetext = self.GetCppInstruction(elem.pInstruct, 0, False)
                    if codetext is None:
                        return None
                    CppText += codetext
                else:
                    print "Internal error: invalid element type %i '%s' in WriteArgument()" % (elem.Type, elem.Text)
                    return None
                lastelem = elem
            return CppText
        else:
            print "Internal error: invalid argument type %i in WriteArgument()" % Arg.ArgType
            return None
        return None # should never reach this point

    def GetCppUserInstruction(self, pInstruct, iIndent):
        cpptext = " " * (iIndent * self.IndentSize)
        cpptext += pInstruct.pProc.CppName + "("
        bFirst = True
        for arg in pInstruct.Arguments:
            if bFirst is True:
                bFirst = False
            else:
                cpptext += ", "
            argtext = self.GetCppArgument(arg)
            if argtext is None:
                return None
            cpptext += argtext
        return cpptext + ")"

    def GetCppBuiltInInstruction(self, pInstruct, iIndent):
        IndentText = " " * (iIndent * self.IndentSize)
        NextIndent = " " * ((iIndent+1) * self.IndentSize)
        NumTypeLetter = self.LogoState.NumType[0]
        CppText = ""
        # get the C++ code for each argument in this instruction
        ArgText = []
        for arg in pInstruct.Arguments:
            if arg.ArgType == ParamType.LISTCODE:
                ArgText.append("")
            else:
                text = self.GetCppArgument(arg)
                if text is None:
                    return None
                ArgText.append(text)
        # now handle the particular instruction
        if pInstruct.pProc.FullName == ".setspecial":                       # .SETSPECIAL
            return ""
        elif pInstruct.pProc.FullName == "back":                            # BACK
            return self.GetCppBuiltinMove(IndentText, pInstruct.Arguments[0], "-")
        elif pInstruct.pProc.FullName == "clean":                           # CLEAN
            CppText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "clearscreen":                     # CLEARSCREEN
            # just move to HOME position and call clean
            CppText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = tt_TurtleDir = 0.0;\n"
            CppText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "for":                             # FOR
            my_temp = self.LogoState.TempIdx
            self.LogoState.TempIdx += 1
            varname = pInstruct.pMakeVar.CppName
            # write code to set the start and limit values for the FOR loop
            CppText += IndentText + "%s start%02i = %s;\n" % (self.LogoState.NumType, my_temp, ArgText[1])
            CppText += IndentText + "%s limit%02i = %s;\n" % (self.LogoState.NumType, my_temp, ArgText[2])
            # write code to set the step size
            if pInstruct.Arguments[3].ArgType == ParamType.NUMBER:
                CodeList = pInstruct.Arguments[4].Elements[0].pInstruct
                CppText += IndentText + "%s step%02i = %s;\n" % (self.LogoState.NumType, my_temp, ArgText[3])
            else:
                CodeList = pInstruct.Arguments[3].Elements[0].pInstruct
                CppText += IndentText + "%s step%02i = start%02i <= limit%02i ? 1.0 : -1.0;\n" % (self.LogoState.NumType, my_temp, my_temp, my_temp)
            # now write the FOR loop
            CppText += IndentText + "for (%s = start%02i; (%s - limit%02i) * step%02i <= 0.0; %s += step%02i)\n" % (varname, my_temp, varname, my_temp, my_temp, varname, my_temp)
            CppText += IndentText + "{\n"
            for instruct in CodeList:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "forever":                         # FOREVER
            my_counter = self.LogoState.LoopIdx
            self.LogoState.LoopIdx += 1
            CppText += IndentText + "for (int loop%02i=1; ; loop%02i++)\n%s{\n" % (my_counter, my_counter, IndentText)
            for instruct in pInstruct.Arguments[0].Elements[0].pInstruct:
                self.LogoState.InnerLoopIdx = my_counter
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
            self.LogoState.InnerLoopIdx = -1
        elif pInstruct.pProc.FullName == "forward":                         # FORWARD
            return self.GetCppBuiltinMove(IndentText, pInstruct.Arguments[0], "+")
        elif pInstruct.pProc.FullName == "home":                            # HOME
            CppText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = tt_TurtleDir = 0.0;\n"
        elif pInstruct.pProc.FullName == "if":                              # IF
            CppText += IndentText + "if (%s)\n" % ArgText[0] + IndentText + "{\n"
            for instruct in pInstruct.Arguments[1].Elements[0].pInstruct:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "left":                            # LEFT
            return self.GetCppBuiltinTurn(IndentText, pInstruct.Arguments[0], "-")
        elif pInstruct.pProc.FullName in ("localmake", "make"):             # LOCALMAKE, MAKE
            CppText += IndentText + pInstruct.pMakeVar.CppName + " = " + ArgText[1] + ";\n"
        elif pInstruct.pProc.FullName == "minus":                           # MINUS
            CppText += "-" + ArgText[0]
        elif pInstruct.pProc.FullName == "output":                          # OUTPUT
            CppText += IndentText + "return %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "penup":                           # PENUP
            CppText += IndentText + "tt_PenDown = false;\n"
        elif pInstruct.pProc.FullName == "pendown":                         # PENDOWN
            CppText += IndentText + "tt_PenDown = true;\n"
        elif pInstruct.pProc.FullName == "penerase":                        # PENERASE
            CppText += IndentText + "tt_PenPaint = false;\n"
            CppText += IndentText + "glColor3ubv(tt_ColorBackground);\n"
        elif pInstruct.pProc.FullName == "penpaint":                        # PENPAINT
            CppText += IndentText + "tt_PenPaint = true;\n"
            CppText += IndentText + "glColor3ubv(tt_ColorPen);\n"
        elif pInstruct.pProc.FullName == "power":                           # POWER
            if self.LogoState.NumType == 'float':
                CppText += "powf(%s, %s)" % (ArgText[0], ArgText[1])
            else:
                CppText += "pow(%s, %s)" % (ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName == "repcount":                        # REPCOUNT
            if self.LogoState.InnerLoopIdx == -1:
                print "Syntax error: REPCOUNT instruction used outside of a FOREVER or REPEAT loop"
                return None
            CppText += "loop%02i" % self.LogoState.InnerLoopIdx
        elif pInstruct.pProc.FullName == "repeat":                          # REPEAT
            my_counter = self.LogoState.LoopIdx
            self.LogoState.LoopIdx += 1
            CppText += IndentText + "for (int loop%02i=1; loop%02i <= %s; loop%02i++)\n" % (my_counter, my_counter, ArgText[0], my_counter)
            CppText += IndentText + "{\n"
            for instruct in pInstruct.Arguments[1].Elements[0].pInstruct:
                self.LogoState.InnerLoopIdx = my_counter
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
            self.LogoState.InnerLoopIdx = -1
        elif pInstruct.pProc.FullName == "right":                           # RIGHT
            return self.GetCppBuiltinTurn(IndentText, pInstruct.Arguments[0], "+")
        elif pInstruct.pProc.FullName == "setbackground":                   # SETBACKGROUND
            codetext = self.GetCppBuiltinSetColor(IndentText, pInstruct.Arguments[0], "tt_ColorBackground")
            if codetext is None:
                return None
            CppText += codetext
            CppText += IndentText + "if (tt_PenPaint == false)\n"
            CppText += IndentText + " " * self.IndentSize + "glColor3ubv(tt_ColorBackground);\n"
        elif pInstruct.pProc.FullName == "setpencolor":                     # SETPENCOLOR
            codetext = self.GetCppBuiltinSetColor(IndentText, pInstruct.Arguments[0], "tt_ColorPen")
            if codetext is None:
                return None
            CppText += codetext
            CppText += IndentText + "if (tt_PenPaint == true)\n"
            CppText += NextIndent + "glColor3ubv(tt_ColorPen);\n"
        elif pInstruct.pProc.FullName == "setpensize":                      # SETPENSIZE
            CppText += IndentText + "glEnd();\n"
            CppText += IndentText + "glLineWidth(%s);\n" % ArgText[0]
            CppText += IndentText + "glBegin(GL_LINES);\n"
        elif pInstruct.pProc.FullName == "setheading":                      # SETHEADING
            CppText += IndentText + "tt_TurtleDir = (%s) * tt_RadDegree;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "setscrunch":                      # SETSCRUNCH
            CppText += IndentText + "tt_ScrunchXY[0] = %s;\n" % ArgText[0]
            CppText += IndentText + "tt_ScrunchXY[1] = %s;\n" % ArgText[1]
        elif pInstruct.pProc.FullName == "setxy":                           # SETXY
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            CppText += NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[1]
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += IndentText + "}\n" + IndentText + "else\n" + IndentText + "{\n"
            CppText += NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            CppText += NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[1]
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "setx":                            # SETX
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += IndentText + "}\n" + IndentText + "else\n" + IndentText + "{\n"
            CppText += NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "sety":                            # SETY
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[0]
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeLetter
            CppText += IndentText + "}\n" + IndentText + "else\n" + IndentText + "{\n"
            CppText += NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[0]
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "stop":                            # STOP
            CppText += IndentText + "return;\n"
        elif pInstruct.pProc.FullName == "window":                          # WINDOW
            CppText += IndentText + "tt_UseWrap = false;\n"
        elif pInstruct.pProc.FullName == "wrap":                            # WRAP
            CppText += IndentText + "tt_UseWrap = true;\n"
        else:
            print "Internal error: built-in instruction named '%s' is not implemented" % pInstruct.Name
            return None
        return CppText

    def GetCppBuiltinSetColor(self, IndentText, Arg, DestColorArray):
        if Arg.ArgType == ParamType.LISTNUM:
            print "Internal error: Lists not yet supported."
            return None
        else: # must be ParamType.NUMBER
            ArgText = self.GetCppArgument(Arg)
            if ArgText is None:
                return None
            if len(Arg.Elements) > 1:
                ArgText = "(" + ArgText + ")"
            CppText = IndentText + "*((int *)%s) = *((int *) tt_Colors[(int) %s & 15]);\n" % (DestColorArray, ArgText)
        return CppText

    def GetCppBuiltinTurn(self, IndentText, Arg, Sign):
        ArgText = self.GetCppArgument(Arg)
        if ArgText is None:
            return None
        if len(Arg.Elements) > 1:
            ArgText = "(" + ArgText + ")"
        CppText = IndentText + "tt_TurtleDir " + Sign + "= " + ArgText + " * tt_RadDegree;\n"
        return CppText

    def GetCppBuiltinMove(self, IndentText, Arg, DirSign):
        NumTypeGL = self.LogoState.NumType[0]
        if NumTypeGL == "f":
            NumTypeMath = "f"
        else:
            NumTypeMath = ""
        NextIndent = IndentText + " " * self.IndentSize
        ScrunchText = ""
        CppText = ""
        # get the code text for the argument
        ArgText = self.GetCppArgument(Arg)
        if ArgText is None:
            return None
        if len(Arg.Elements) > 1:
            ArgText = "(" + ArgText + ")"
        # write expression to calculate the new X position
        if self.LogoState.bUseScrunch:
            ScrunchText = " * tt_ScrunchXY[0]"
        NewXText = "tt_TurtlePos[0] %s sin%s(tt_TurtleDir) * %s%s;\n" % (DirSign, NumTypeMath, ArgText, ScrunchText)
        # write expression to calculate the new Y position
        if self.LogoState.bUseScrunch:
            ScrunchText = " * tt_ScrunchXY[1]"
        NewYText = "tt_TurtlePos[1] %s cos%s(tt_TurtleDir) * %s%s;\n" % (DirSign, NumTypeMath, ArgText, ScrunchText)
        # write code to draw the line
        if self.LogoState.bUseWrap:
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "%s NewPos[2];\n" % self.LogoState.NumType
            CppText += NextIndent + "NewPos[0] = " + NewXText
            CppText += NextIndent + "NewPos[1] = " + NewYText
            CppText += NextIndent + "wrapper_DrawLineSegment(tt_TurtlePos, NewPos, tt_UseWrap);\n"
            CppText += NextIndent + "tt_TurtlePos[0] = NewPos[0];\n" + NextIndent + "tt_TurtlePos[1] = NewPos[1];\n"
            CppText += IndentText + "} else {\n"
        else:
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeGL
            CppText += NextIndent + "tt_TurtlePos[0] = " + NewXText
            CppText += NextIndent + "tt_TurtlePos[1] = " + NewYText
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeGL
            CppText += IndentText + "} else {\n"
        # write code for the PenUp case
        CppText += NextIndent + "tt_TurtlePos[0] = " + NewXText
        CppText += NextIndent + "tt_TurtlePos[1] = " + NewYText
        CppText += IndentText + "}\n"
        return CppText


