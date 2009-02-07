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
#include <time.h>
#include <SDL.h>
#include <SDL_opengl.h>
#include "wrapper_api.h"
#include "wrapper_clist.h"
#include "wrapper_carray.h"
#include "wrapper_pointtext.h"

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
        self.LogoState.iLineSmooth = 2
        self.LogoState.fFramesPerSec = 0.0
        self.LogoState.bUseScrunch = False
        self.LogoState.bUseWrap = False
        self.LogoState.bNeedLabel = False
        self.LogoState.bNeedColors = False
        self.LogoState.bNeedRandom = False
        self.LogoState.bNeedGaussian = False
        self.LogoState.bNeedTowardsFunc = False
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
            elif specialname == 'framespersec':
                self.LogoState.fFramesPerSec = specialnum
            elif specialname == 'linesmooth':
                self.LogoState.iLineSmooth = int(specialnum)
            else:
                print "Warning: .setspecial instruction used with unknown variable '%s'" % specialname
        elif pInstruct.Name.lower() in ('setpencolor', 'setpc', 'setbackground', 'setbg') and pInstruct.Arguments[0].ArgType == ParamType.NUMBER:
            self.LogoState.bNeedColors = True
        elif pInstruct.Name.lower() == 'setscrunch':
            self.LogoState.bUseScrunch = True
        elif pInstruct.Name.lower() in ('wrap', 'window'):
            self.LogoState.bUseWrap = True
        elif pInstruct.Name.lower() == 'towards' and pInstruct.Arguments[0].Elements[0].Type != ElemType.NUMBER:
            self.LogoState.bNeedTowardsFunc = True
        elif pInstruct.Name.lower() == 'random':
            self.LogoState.bNeedRandom = True
        elif pInstruct.Name.lower() == 'gaussian':
            self.LogoState.bNeedGaussian = True
        elif pInstruct.Name.lower() in ('label', 'setfont', 'setfontheight', 'setjustifyvert', 'setjustifyhorz'):
            self.LogoState.bNeedLabel = True
        return True

    # Write out the global variables for the CPP code
    def WriteGlobals(self, GlobalVariables):
        IndentText = " " * self.IndentSize
        NumTypeMath = ""
        if self.LogoState.NumType == 'float':
            NumTypeMath = "f"
        self.OutputText += "// Static TurboTurtle data, only used by code in this source file\n"
        # start by writing the special TurboTurtle variables
        self.OutputText += "static const %s tt_DegreeRad = 180.0 / 3.141592653589793;\n" % self.LogoState.NumType
        self.OutputText += "static const %s tt_RadDegree = 3.141592653589793 / 180.0;\n" % self.LogoState.NumType
        # the home position is 0.5,0.5 because this is in the middle of the pixel
        # if we use 0,0 here the round-off errors of 'float's will cause artifacts
        self.OutputText += "static %s tt_TurtlePos[2] = {0.5, 0.5};\n" % self.LogoState.NumType
        self.OutputText += "static %s tt_TurtleDir = 0.0;\n" % self.LogoState.NumType
        self.OutputText += "static bool tt_PenDown = true;\n"
        self.OutputText += "static bool tt_PenPaint = true;\n"
        self.OutputText += "static bool tt_TestValue = false;\n"
        self.OutputText += "\n// Global TurboTurtle data, also readable and writable by the wrapper\n"
        self.OutputText += "float tt_FramesPerSec = %f;\n" % self.LogoState.fFramesPerSec
        self.OutputText += "int tt_LineSmooth = %i;\n" % self.LogoState.iLineSmooth
        self.OutputText += "int tt_WindowSize = %i;\n" % self.LogoState.iWindowSize
        self.OutputText += "unsigned char tt_ColorPen[4] = {255,255,255,0};\n"
        self.OutputText += "unsigned char tt_ColorBackground[4] = {0,0,0,0};\n"
        if self.LogoState.bNeedColors:
            self.OutputText += "unsigned char tt_Colors[16][4] = {{0,0,0,0}, {0,0,255,0}, {0,255,0,0}, {0,255,255,0}, {255,0,0,0}, {255,0,255,0}, {255,255,0,0}, {255,255,255,0}, {160,82,45,0}, {210,180,140,0}, {34,139,34,0}, {127,255,212,0}, {250,128,114,0}, {128,0,128,0}, {255,165,0,0}, {128,128,128,0}};\n"
        if self.LogoState.bUseScrunch:
            self.OutputText += "%s tt_ScrunchXY[2] = {1.0, 1.0};\n" % self.LogoState.NumType
        if self.LogoState.bUseWrap:
            self.OutputText += "bool tt_UseWrap = false;\n"
        if self.LogoState.bNeedLabel:
            self.OutputText += "int tt_Font=0, tt_JustifyVert=0, tt_JustifyHorz=0;\n"
            self.OutputText += "float tt_FontHeight=%f;\n" % float(self.LogoState.iWindowSize/25.0)
            self.OutputText += "char tt_LabelText[1024];\n"
        self.OutputText += "\n"
        # then write out definitions for static functions which might be used by the logo code
        if self.LogoState.bNeedTowardsFunc:
            self.OutputText += "static %s tt_Towards(const CList<%s> &list)\n{\n" % (self.LogoState.NumType, self.LogoState.NumType)
            self.OutputText += IndentText + "return atan2(list[0] - tt_TurtlePos[0], list[1] - tt_TurtlePos[1]) * tt_DegreeRad;\n}\n\n"
        if self.LogoState.bNeedRandom:
            self.OutputText += "static int tt_Random(int iRange)\n{\n"
            self.OutputText += IndentText + "return ((long long) iRange * rand() / ((long long) RAND_MAX + 1));\n}\n"
            self.OutputText += "static int tt_Random(int iStart, int iEnd)\n{\n"
            self.OutputText += IndentText + "return iStart + ((long long) (iEnd - iStart + 1) * rand() / ((long long) RAND_MAX + 1));\n}\n\n"
        if self.LogoState.bNeedGaussian:
            self.OutputText += "static %s tt_Gaussian(void)\n{\n" % self.LogoState.NumType
            self.OutputText += IndentText + "static bool bHaveOne = false;\n"
            self.OutputText += IndentText + "static %s u2;\n" % self.LogoState.NumType
            self.OutputText += IndentText + "%s x1, x2, w, u1;\n" % self.LogoState.NumType
            self.OutputText += IndentText + "if (bHaveOne) { bHaveOne = false; return u2; }\n"
            self.OutputText += IndentText + "do {\n"
            self.OutputText += IndentText * 2 + "x1 = 2.0 * (((%s) rand() + 1.0) / ((%s) RAND_MAX + 2.0)) - 1.0;\n" % (self.LogoState.NumType, self.LogoState.NumType)
            self.OutputText += IndentText * 2 + "x2 = 2.0 * (((%s) rand() + 1.0) / ((%s) RAND_MAX + 2.0)) - 1.0;\n" % (self.LogoState.NumType, self.LogoState.NumType)
            self.OutputText += IndentText * 2 + "w = x1 * x1 + x2 * x2;\n"
            self.OutputText += IndentText + "} while (w >= 1.0);\n"
            self.OutputText += IndentText + "w = sqrt%s((-2.0 * log%s(w)) / w);\n" % (NumTypeMath, NumTypeMath)
            self.OutputText += IndentText + "u1 = x1 * w;\n"
            self.OutputText += IndentText + "u2 = x2 * w;\n"
            self.OutputText += IndentText + "bHaveOne = true;\n"
            self.OutputText += IndentText + "return u1;\n}\n\n"
        # generate a string of C++ definitions for the Logo program's global variables
        InitCode = ""
        if len(GlobalVariables) > 0:
            self.OutputText += "// Global variable definitions for Logo program\n"
            for var in GlobalVariables:
                Code = self.WriteVariableDefinition(var, 0)
                if Code is None:
                    return None
                InitCode += Code
            self.OutputText += "\n"
        # add any extra program initialization code to run at the beginning of tt_LogoMain()
        if self.LogoState.bNeedRandom:
            InitCode += IndentText + "srand((unsigned int) time(NULL));\n"
        if len(InitCode) > 0:
            InitCode += "\n"
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
            if not self.WriteVarType(var.Type, var.ArrayDim):
                return False
            self.OutputText += " " + var.CppName
        self.OutputText += ")"
        return True

    # Write out variable definition
    def WriteVariableDefinition(self, Var, iIndent):
        InitCode = ""
        # write leading white space, the variable's C++ type, and name
        self.OutputText += " " * (iIndent * self.IndentSize)
        if not self.WriteVarType(Var.Type, Var.ArrayDim):
            return None
        self.OutputText += " " + Var.CppName
        # next write initialization code
        if Var.Type == ParamType.BOOLEAN:
            self.OutputText += " = false;\n"
        elif Var.Type == ParamType.NUMBER:
            self.OutputText += " = 0.0;\n"
        elif Var.Type in (ParamType.LISTNUM, ParamType.ARRAY):
            self.OutputText += ";\n"
        elif Var.Type == ParamType.QUOTEDWORD:
            self.OutputText += ' = "";\n'
        else:
            print "Internal error: invalid variable type %i in WriteVariableDefinition()" % Var.Type
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

    def WriteVarType(self, Type, ArrayDim=None):
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
            self.OutputText += "CList<%s>" % self.LogoState.NumType
            return True
        elif Type == ParamType.ARRAY:
            self.OutputText += "CArray<%s,%i>" % (self.LogoState.NumType, ArrayDim or 2)
            return True
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

    def GetCppSafeString(self, instring):
        instring = instring.replace("\\", "\\\\")
        instring = instring.replace('"', '\\"')
        return instring

    def GetCppArgument(self, Arg):
        CppText = ""
        if Arg.ArgType == ParamType.ARRAY:
            if Arg.Elements[0].Type == ElemType.VAR_VALUE:
                return Arg.Elements[0].pVariable.CppName
            elif Arg.Elements[0].Type == ElemType.FUNC_CALL:
                return self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
            else:
                print "Internal error: invalid ARRAY element '%s' in GetCppArgument()" % elem.Text
                return None
        elif Arg.ArgType == ParamType.QUOTEDWORD:
            if Arg.Elements[0].Type == ElemType.QUOTED_WORD:
                return '"' + self.GetCppSafeString(Arg.Elements[0].Text[1:]) + '"'
            elif Arg.Elements[0].Type == ElemType.VAR_VALUE:
                return Arg.Elements[0].pVariable.CppName
            elif Arg.Elements[0].Type == ElemType.FUNC_CALL:
                return self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
            else:
                print "Internal error: invalid QUOTEDWORD element '%s' in GetCppArgument()" % elem.Text
                return None
        elif Arg.ArgType == ParamType.LISTNUM:
            if Arg.Elements[0].Type == ElemType.NUMBER:
                CppText += "CList<%s>(" % self.LogoState.NumType
                if len(Arg.Elements) <= 4:
                    bFirst = True
                    for elem in Arg.Elements:
                        if bFirst == True:
                            bFirst = False
                        else:
                            CppText += ", "
                        CppText += elem.Text
                else:
                    CppText += "%i" % len(Arg.Elements)
                    for elem in Arg.Elements:
                        CppText += ", (double) %s" % elem.Text
                return CppText + ")"
            elif Arg.Elements[0].Type == ElemType.VAR_VALUE:
                return Arg.Elements[0].pVariable.CppName
            elif Arg.Elements[0].Type == ElemType.FUNC_CALL:
                return self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
            else:
                print "Internal error: invalid LISTNUM element '%s' in GetCppArgument()" % elem.Text
                return None
        elif Arg.ArgType in (ParamType.NUMBER, ParamType.BOOLEAN):
            lastelem = None
            for elem in Arg.Elements:
                if elem.Type in (ElemType.OPEN_PAREN, ElemType.CLOSE_PAREN, ElemType.NUMBER):
                    CppText += elem.Text
                elif elem.Type == ElemType.BOOLEAN:
                    CppText += elem.Text.lower()
                elif elem.Type == ElemType.INFIX_BOOL:
                    if elem.Text in ("<", ">", "<=", ">="):
                        CppText += " " + elem.Text + " "
                    elif elem.Text == "=":
                        CppText += " == "
                    elif elem.Text == "<>":
                        CppText += " != "
                    else:
                        print "Internal error: invalid INFIX_BOOL element '%s' in GetCppArgument()" % elem.Text
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
                    print "Internal error: invalid element type %i '%s' in GetCppArgument()" % (elem.Type, elem.Text)
                    return None
                lastelem = elem
            return CppText
        else:
            print "Internal error: invalid argument type %i in GetCppArgument()" % Arg.ArgType
            return None
        return None # should never reach this point

    # this is used for MDARRAY, MDITEM, and MDSETITEM instructions, to generate argument list for call to CArray object
    def GetCppListnumExpansion(self, Arg, Count, InstructName):
        CppText = ""
        if Arg.Elements[0].Type == ElemType.NUMBER:
            if len(Arg.Elements) != Count:
                print "Syntax error: %s instruction expects input list with %i dimensions, but %i given" % (InstructName, Count, len(Arg.Elements))
                return None
            for i in range(Count):
                if i != 0:
                    CppText += ", "
                CppText += "%i" % int(Arg.Elements[i].Text)
            return CppText
        elif Arg.Elements[0].Type == ElemType.VAR_VALUE:
            for i in range(Count):
                if i != 0:
                    CppText += ", "
                CppText += "(int) %s[%i]" % (Arg.Elements[0].pVariable.CppName, i)
            return CppText
        elif Arg.Elements[0].Type == ElemType.FUNC_CALL:
            if Arg.Elements[0].pInstruct.Name.lower() != "list":
                print "Internal error: non-LIST function call in LISTNUM expansion"
                return None
            listinstruct = Arg.Elements[0].pInstruct
            if len(listinstruct.Arguments) != Count:
                print "Syntax error: %s instruction expects input list with %i dimensions, but %i given" % (InstructName, Count, len(listinstruct.Arguments))
                return None
            for i in range(Count):
                if i != 0:
                    CppText += ", "
                cpparg = self.GetCppArgument(listinstruct.Arguments[i])
                if cpparg is None:
                    return None
                CppText += "(int) (%s)" % cpparg
            return CppText
        print "Internal error: invalid element type '%s' in GetCppListnumExpansion" % ElemType.Names[Arg.Elements[0].Type]
        return None

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
        NumTypeGL = self.LogoState.NumType[0]
        NumTypeMath = ""
        if self.LogoState.NumType == 'float':
            NumTypeMath = "f"
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
        elif pInstruct.pProc.FullName == "abs":                             # ABS
            CppText += "fabs%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "and":                             # AND
            bFirst = True
            for argtext in ArgText:
                if bFirst is True:
                    bFirst = False
                else:
                    CppText += " && "
                CppText += "(%s)" % argtext
        elif pInstruct.pProc.FullName == "arctan":                          # ARCTAN
            if len(ArgText) == 1:
                CppText += "atan%s(%s) * tt_DegreeRad" % (NumTypeMath, ArgText[0])
            else:
                CppText += "atan2%s(%s, %s) * tt_DegreeRad" % (NumTypeMath, ArgText[1], ArgText[0])
        elif pInstruct.pProc.FullName == "array":                           # ARRAY
            CppText += "CArray<%s,1>(" % self.LogoState.NumType
            if len(pInstruct.Arguments) == 1:
                CppText += "(int) (%s), 1" % ArgText[0]
            else:
                CppText += "(int) (%s), (int) (%s)" % (ArgText[0], ArgText[1])
            CppText += ")"
        elif pInstruct.pProc.FullName == "back":                            # BACK
            return self.GetCppBuiltinMove(IndentText, pInstruct.Arguments[0], "-")
        elif pInstruct.pProc.FullName == "butfirst":                        # BUTFIRST
            CppText += "%s.ButFirst()" % ArgText[0]
        elif pInstruct.pProc.FullName == "butlast":                         # BUTLAST
            CppText += "%s.ButLast()" % ArgText[0]
        elif pInstruct.pProc.FullName == "clean":                           # CLEAN
            CppText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "clearscreen":                     # CLEARSCREEN
            # just move to HOME position and call clean
            CppText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = 0.5;\n"
            CppText += IndentText + "tt_TurtleDir = 0.0;\n"
            CppText += IndentText + "wrapper_Clean();\n"
        elif pInstruct.pProc.FullName == "cos":                             # COS
            CppText += "cos%s((%s) * tt_RadDegree)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "count":                           # COUNT
            CppText += "%s.Length()" % ArgText[0]
        elif pInstruct.pProc.FullName == "difference":                      # DIFFERENCE
            CppText += "(%s) - (%s)" % (ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName in ("do.while", "do.until"):          # DO.WHILE, DO.UNTIL
            CppText += IndentText + "do {\n"
            for instruct in pInstruct.Arguments[0].Elements[0].pInstruct:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            if pInstruct.pProc.FullName == "do.while":
                CppText += IndentText + "} while (%s);\n" % ArgText[1]
            else:
                CppText += IndentText + "} while (!(%s));\n" % ArgText[1]
        elif pInstruct.pProc.FullName == "emptyp":                          # EMPTYP
            CppText += "%s.Length() == 0" % ArgText[0]
        elif pInstruct.pProc.FullName == "erasescreen":                     # ERASESCREEN
            CppText += IndentText + "wrapper_Erase();\n"
        elif pInstruct.pProc.FullName == "exp":                             # EXP
            CppText += "exp%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "first":                           # FIRST
            CppText += "%s[0]" % ArgText[0]
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
        elif pInstruct.pProc.FullName == "fput":                            # FPUT
            CppText += "CList<%s>(%s, %s)" % (self.LogoState.NumType, ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName == "gaussian":                        # GAUSSIAN
            CppText += "tt_Gaussian()"
        elif pInstruct.pProc.FullName == "goto":                            # GOTO
            CppText += IndentText + "goto tag_%s;\n" % ArgText[0][1:-1]
        elif pInstruct.pProc.FullName == "heading":                         # HEADING
            CppText += "(tt_TurtleDir < 0.0 ? 360.0+fmod(tt_TurtleDir,360.0) : fmod(tt_TurtleDir,360.0))"
        elif pInstruct.pProc.FullName == "home":                            # HOME
            CppText += IndentText + "tt_TurtlePos[0] = tt_TurtlePos[1] = 0.5;\n"
            CppText += IndentText + "tt_TurtleDir = 0.0;\n"
        elif pInstruct.pProc.FullName in ("if", "ifelse"):                  # IF, IFELSE
            CppText += IndentText + "if (%s)\n" % ArgText[0] + IndentText + "{\n"
            for instruct in pInstruct.Arguments[1].Elements[0].pInstruct:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            if pInstruct.pProc.FullName == "if":
                CppText += IndentText + "}\n"
            else:
                CppText += IndentText + "} else {\n"
                for instruct in pInstruct.Arguments[2].Elements[0].pInstruct:
                    codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                    if codetext is None:
                        return None
                    CppText += codetext
                CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName in ("iftrue", "iffalse"):             # IFTRUE, IFFALSE
            if pInstruct.pProc.FullName == "iftrue":
                CppText += IndentText + "if (tt_TestValue)\n" + IndentText + "{\n"
            else:
                CppText += IndentText + "if (!tt_TestValue)\n" + IndentText + "{\n"
            for instruct in pInstruct.Arguments[0].Elements[0].pInstruct:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "int":                             # INT
            CppText += "(int) (%s)" % ArgText[0]
        elif pInstruct.pProc.FullName == "item":                            # ITEM
            if pInstruct.Arguments[1].ArgType == ParamType.LISTNUM:
                CppText += "%s[(int) (%s)-1]" % (ArgText[1], ArgText[0])
            elif pInstruct.Arguments[1].ArgType == ParamType.ARRAY:
                CppText += "%s.Get((int) (%s))" % (ArgText[1], ArgText[0])
        elif pInstruct.pProc.FullName == "label":                           # LABEL
            CppText += IndentText + "glEnd();\n"
            CppText += IndentText + "sprintf(tt_LabelText, \""
            bFirst = True
            for arg in pInstruct.Arguments:
                if bFirst is True:
                    bFirst = False
                else:
                    CppText += " "
                if arg.ArgType == ParamType.QUOTEDWORD or arg.ArgType == ParamType.BOOLEAN:
                    CppText += "%s"
                elif arg.ArgType == ParamType.NUMBER:
                    CppText += "%g"
                else:
                    print "Syntax error: Invalid parameter type %i (%s) in LABEL instruction." % (arg.ArgType, ParamType.Names[arg.ArgType])
                    return None
            CppText += "\""
            for i in range(len(pInstruct.Arguments)):
                arg = pInstruct.Arguments[i]
                CppText += ", "
                if arg.ArgType == ParamType.QUOTEDWORD:
                    CppText += ArgText[i]
                elif arg.ArgType == ParamType.NUMBER:
                    CppText += "(double) (%s)" % ArgText[i]
                elif arg.ArgType == ParamType.BOOLEAN:
                    CppText += '(%s) ? "True" : "False"' % ArgText[i]
            CppText += ");\n"
            CppText += IndentText + "DrawPointText(tt_Font, tt_JustifyVert, tt_JustifyHorz, tt_FontHeight, tt_TurtlePos[0], tt_TurtlePos[1], tt_LabelText);\n"
            CppText += IndentText + "glBegin(GL_LINES);\n"
        elif pInstruct.pProc.FullName == "last":                            # LAST
            CppText += "%s.Last()" % ArgText[0]
        elif pInstruct.pProc.FullName == "left":                            # LEFT
            CppText += IndentText + "tt_TurtleDir -= %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "list":                            # LIST
            CppText += "CList<%s>(" % self.LogoState.NumType
            if len(pInstruct.Arguments) <= 4:
                for i in range(len(pInstruct.Arguments)):
                    if i != 0:
                        CppText += ", "
                    CppText += ArgText[i]
            else:
                CppText += "%i" % len(pInstruct.Arguments)
                for i in range(len(pInstruct.Arguments)):
                    CppText += ", (double) %s" % ArgText[i]
            CppText += ")"
        elif pInstruct.pProc.FullName == "ln":                              # LN
            CppText += "log%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName in ("localmake", "make"):             # LOCALMAKE, MAKE
            CppText += IndentText + pInstruct.pMakeVar.CppName + " = " + ArgText[1] + ";\n"
        elif pInstruct.pProc.FullName == "log10":                           # LOG10
            CppText += "log10%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "lput":                            # FPUT
            CppText += "CList<%s>(%s, %s)" % (self.LogoState.NumType, ArgText[1], ArgText[0])
        elif pInstruct.pProc.FullName == "mdarray":                         # MDARRAY
            if pInstruct.ReturnArrayDim is None:
                print "Internal error: unknown array dimensions for 'MDARRAY %s'" % ArgText[0]
                return None
            if pInstruct.ReturnArrayDim < 2 or pInstruct.ReturnArrayDim > 3:
                print "Logical error: MDARRAY cannot create an array with %i dimensions" % pInstruct.ReturnArrayDim
                return None
            listargtext = self.GetCppListnumExpansion(pInstruct.Arguments[0], pInstruct.ReturnArrayDim, "MDARRAY")
            if listargtext == None:
                return None
            CppText += "CArray<%s,%i>(%s)" % (self.LogoState.NumType, pInstruct.ReturnArrayDim, listargtext)
        elif pInstruct.pProc.FullName == "mditem":                          # MDITEM
            if pInstruct.Arguments[1].Elements[0].Type != ElemType.VAR_VALUE:
                print "Syntax error: MDITEM requires a variable for the array input, but '%s' was given" % pInstruct.Arguments[1].Elements[0].Text
                return None
            ArrayDim = pInstruct.Arguments[1].Elements[0].pVariable.ArrayDim
            if ArrayDim < 2:
                print "Logical error: Array '%s' in MDITEM instruction has fewer than 2 dimensions" % pInstruct.Arguments[1].Elements[0].Text
                return None
            listargtext = self.GetCppListnumExpansion(pInstruct.Arguments[0], ArrayDim, "MDITEM")
            if listargtext == None:
                return None
            CppText += "%s.Get(%s)" % (ArgText[1], listargtext)
        elif pInstruct.pProc.FullName == "mdsetitem":                       # MDSETITEM
            if pInstruct.Arguments[1].Elements[0].Type != ElemType.VAR_VALUE:
                print "Syntax error: MDSETITEM requires a variable for the array input, but '%s' was given" % pInstruct.Arguments[1].Elements[0].Text
                return None
            ArrayDim = pInstruct.Arguments[1].Elements[0].pVariable.ArrayDim
            if ArrayDim < 2:
                print "Logical error: Array '%s' in MDSETITEM instruction has fewer than 2 dimensions" % pInstruct.Arguments[1].Elements[0].Text
                return None
            listargtext = self.GetCppListnumExpansion(pInstruct.Arguments[0], ArrayDim, "MDSETITEM")
            if listargtext == None:
                return None
            CppText += IndentText + "%s.Set(%s, %s);\n" % (ArgText[1], ArgText[2], listargtext)
        elif pInstruct.pProc.FullName == "minus":                           # MINUS
            CppText += "-(%s)" % ArgText[0]
        elif pInstruct.pProc.FullName == "not":                             # NOT
            CppText += "!(%s)" % ArgText[0]
        elif pInstruct.pProc.FullName == "or":                              # OR
            bFirst = True
            for argtext in ArgText:
                if bFirst is True:
                    bFirst = False
                else:
                    CppText += " || "
                CppText += "(%s)" % argtext
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
        elif pInstruct.pProc.FullName == "pick":                            # PICK
            CppText += "%s.Pick()" % ArgText[0]
        elif pInstruct.pProc.FullName == "pos":                             # POS
            CppText += "CList<%s>(tt_TurtlePos[0], tt_TurtlePos[1])" % self.LogoState.NumType
        elif pInstruct.pProc.FullName == "power":                           # POWER
            CppText += "pow%s(%s, %s)" % (NumTypeMath, ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName == "product":                         # PRODUCT
            CppText += "(%s)" % ArgText[0]
            for argtext in ArgText[1:]:
                CppText += " * (%s)" % argtext
        elif pInstruct.pProc.FullName == "quotient":                        # QUOTIENT
            if len(ArgText) == 1:
                CppText += "1.0 / (%s)" % ArgText[0]
            else:
                CppText += "(%s) / (%s)" % (ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName == "radarctan":                       # RADARCTAN
            if len(ArgText) == 1:
                CppText += "atan%s(%s)" % (NumTypeMath, ArgText[0])
            else:
                CppText += "atan2%s(%s, %s)" % (NumTypeMath, ArgText[1], ArgText[0])
        elif pInstruct.pProc.FullName == "radcos":                          # RADCOS
            CppText += "cos%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "radsin":                          # RADSIN
            CppText += "sin%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "random":                          # RANDOM
            if len(ArgText) == 1:
                CppText += "tt_Random((int) (%s))" % ArgText[0]
            else:
                CppText += "tt_Random((int) (%s), (int) (%s))" % (ArgText[0], ArgText[1])
        elif pInstruct.pProc.FullName == "remainder":                       # REMAINDER
            CppText += "(int) (%s) %% (int) (%s)" % (ArgText[0], ArgText[1])
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
        elif pInstruct.pProc.FullName == "rerandom":                        # RERANDOM
            if len(ArgText) == 0:
                CppText += IndentText + "srand(0);\n"
            else:
                CppText += IndentText + "srand((int) (%s));\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "reverse":                         # REVERSE
            CppText += "%s.Reverse()" % ArgText[0]
        elif pInstruct.pProc.FullName == "right":                           # RIGHT
            CppText += IndentText + "tt_TurtleDir += %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "round":                           # ROUND
            CppText += "round%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "setbackground":                   # SETBACKGROUND
            codetext = self.GetCppBuiltinSetColor(IndentText, pInstruct.Arguments[0], "tt_ColorBackground")
            if codetext is None:
                return None
            CppText += codetext
            CppText += IndentText + "if (tt_PenPaint == false)\n"
            CppText += IndentText + " " * self.IndentSize + "glColor3ubv(tt_ColorBackground);\n"
        elif pInstruct.pProc.FullName == "setfont":                         # SETFONT
            CppText += IndentText + "tt_Font = %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "setfontheight":                   # SETFONTHEIGHT
            CppText += IndentText + "tt_FontHeight = %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "setheading":                      # SETHEADING
            CppText += IndentText + "tt_TurtleDir = %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "setitem":                         # SETITEM
            if pInstruct.Arguments[1].Elements[0].Type != ElemType.VAR_VALUE:
                print "Syntax error: destination array for SETITEM instruction can only be a variable"
                return None
            if pInstruct.Arguments[1].Elements[0].pVariable.ArrayDim != 1:
                print "Logical error: Array '%s' in SETITEM instruction is not 1-dimensional" % pInstruct.Arguments[1].Elements[0].Text
                return None
            CppText += IndentText + "%s.Set(%s, (int) (%s));\n" % (ArgText[1], ArgText[2], ArgText[0])
        elif pInstruct.pProc.FullName == "setjustifyvert":                  # SETJUSTIFYVERT
            CppText += IndentText + "tt_JustifyVert = %s;\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "setjustifyhorz":                  # SETJUSTIFYHORZ
            CppText += IndentText + "tt_JustifyHorz = %s;\n" % ArgText[0]
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
        elif pInstruct.pProc.FullName == "setpos":                          # SETPOS
            Arg = pInstruct.Arguments[0]
            elem0type = Arg.Elements[0].Type
            UpdateTurtle = ""
            if elem0type == ElemType.NUMBER:
                if len(Arg.Elements) != 2:
                    print "Syntax error: SETPOS instruction takes an immediate list with exactly 2 numbers, but %i were given." % len(Arg.Elements)
                    return None
                for i in range(2):
                    UpdateTurtle += NextIndent + "tt_TurtlePos[%i] = %s;\n" % (i, Arg.Elements[i].Text)
            elif elem0type == ElemType.VAR_VALUE:
                UpdateTurtle += NextIndent + "tt_TurtlePos[0] = %s[0];\n" % (Arg.Elements[0].pVariable.CppName)
                UpdateTurtle += NextIndent + "tt_TurtlePos[1] = %s[1];\n" % (Arg.Elements[0].pVariable.CppName)
            elif elem0type == ElemType.FUNC_CALL:
                my_temp = self.LogoState.TempIdx
                self.LogoState.TempIdx += 1
                codetext = self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
                if codetext is None:
                    return None
                UpdateTurtle += NextIndent + "CList<%s> templist%02i = %s;\n" % (self.LogoState.NumType, my_temp, codetext)
                UpdateTurtle += NextIndent + "tt_TurtlePos[0] = templist%02i[0];\n" % my_temp
                UpdateTurtle += NextIndent + "tt_TurtlePos[1] = templist%02i[1];\n" % my_temp
            else:
                print "Internal error: invalid element type %i '%s' in a List argument for SETPOS." % (elem0type, ElemType.Names[elem0type])
                return None
            CppText += self.GetCppBuiltinJump(IndentText, UpdateTurtle)
        elif pInstruct.pProc.FullName == "setscrunch":                      # SETSCRUNCH
            CppText += IndentText + "tt_ScrunchXY[0] = %s;\n" % ArgText[0]
            CppText += IndentText + "tt_ScrunchXY[1] = %s;\n" % ArgText[1]
        elif pInstruct.pProc.FullName == "setxy":                           # SETXY
            UpdateTurtle =  NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            UpdateTurtle += NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[1]
            CppText += self.GetCppBuiltinJump(IndentText, UpdateTurtle)
        elif pInstruct.pProc.FullName == "setx":                            # SETX
            UpdateTurtle = NextIndent + "tt_TurtlePos[0] = %s;\n" % ArgText[0]
            CppText += self.GetCppBuiltinJump(IndentText, UpdateTurtle)
        elif pInstruct.pProc.FullName == "sety":                            # SETY
            UpdateTurtle = NextIndent + "tt_TurtlePos[1] = %s;\n" % ArgText[0]
            CppText += self.GetCppBuiltinJump(IndentText, UpdateTurtle)
        elif pInstruct.pProc.FullName == "sin":                             # SIN
            CppText += "sin%s((%s) * tt_RadDegree)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "sqrt":                            # SQRT
            CppText += "sqrt%s(%s)" % (NumTypeMath, ArgText[0])
        elif pInstruct.pProc.FullName == "stop":                            # STOP
            CppText += IndentText + "return;\n"
        elif pInstruct.pProc.FullName == "sum":                             # SUM
            CppText += "(%s)" % ArgText[0]
            for argtext in ArgText[1:]:
                CppText += " + (%s)" % argtext
        elif pInstruct.pProc.FullName == "tag":                             # TAG
            CppText += "tag_%s:\n" % ArgText[0][1:-1]
        elif pInstruct.pProc.FullName == "test":                            # TEST
            CppText += IndentText + "tt_TestValue = (bool) (%s);\n" % ArgText[0]
        elif pInstruct.pProc.FullName == "towards":                         # TOWARDS
            Arg = pInstruct.Arguments[0]
            elem0type = Arg.Elements[0].Type
            if elem0type == ElemType.NUMBER:
                if len(Arg.Elements) != 2:
                    print "Syntax error: TOWARDS instruction takes an immediate list with exactly 2 numbers, but %i were given." % len(Arg.Elements)
                    return None
                CppText += "(atan2(%s - tt_TurtlePos[0], %s - tt_TurtlePos[1])*tt_DegreeRad)" % (Arg.Elements[0].Text, Arg.Elements[1].Text)
            elif elem0type == ElemType.VAR_VALUE:
                CppText += "tt_Towards(%s)" % Arg.Elements[0].pVariable.CppName
            elif elem0type == ElemType.FUNC_CALL:
                codetext = self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
                if codetext is None:
                    return None
                CppText += "tt_Towards(%s)" % codetext
            else:
                print "Internal error: invalid element type %i '%s' in a List argument for TOWARDS." % (elem0type, ElemType.Names[elem0type])
                return None
        elif pInstruct.pProc.FullName == "wait":                            # WAIT
            CppText += IndentText + "SDL_Delay((int) ((%s) * 1000 / 60));\n" % ArgText[0]
        elif pInstruct.pProc.FullName in ("while", "until"):                # WHILE, UNTIL
            if pInstruct.pProc.FullName == "while":
                CppText += IndentText + "while (%s) {\n" % ArgText[0]
            else:
                CppText += IndentText + "while (!(%s)) {\n" % ArgText[0]
            for instruct in pInstruct.Arguments[1].Elements[0].pInstruct:
                codetext = self.GetCppInstruction(instruct, iIndent + 1, True)
                if codetext is None:
                    return None
                CppText += codetext
            CppText += IndentText + "}\n"
        elif pInstruct.pProc.FullName == "window":                          # WINDOW
            CppText += IndentText + "tt_UseWrap = false;\n"
        elif pInstruct.pProc.FullName == "wrap":                            # WRAP
            CppText += IndentText + "tt_UseWrap = true;\n"
        elif pInstruct.pProc.FullName == "xcor":                            # XCOR
            CppText += "tt_TurtlePos[0]"
        elif pInstruct.pProc.FullName == "ycor":                            # YCOR
            CppText += "tt_TurtlePos[1]"
        else:
            print "Internal error: built-in instruction named '%s' is not implemented" % pInstruct.Name
            return None
        return CppText

    def GetCppBuiltinSetColor(self, IndentText, Arg, DestColorArray):
        if Arg.ArgType == ParamType.LISTNUM:
            CppText = ""
            elem0type = Arg.Elements[0].Type
            if elem0type == ElemType.NUMBER:
                if len(Arg.Elements) != 3:
                    print "Syntax error: SETPC/SETBG instruction takes an immediate list with exactly 3 numbers, but %i were given." % len(Arg.Elements)
                    return None
                for i in range(3):
                    color = int(Arg.Elements[i].Text)
                    if color < 0 or color > 255:
                        print "Syntax error: invalid color component value %i in SETPC/SETBG instruction" % color
                        return None
                    CppText += IndentText + "%s[%i] = %i;\n" % (DestColorArray, i, color)
            elif elem0type == ElemType.VAR_VALUE:
                CppText += IndentText + "%s[0] = (unsigned char) %s[0];\n" % (DestColorArray, Arg.Elements[0].pVariable.CppName)
                CppText += IndentText + "%s[1] = (unsigned char) %s[1];\n" % (DestColorArray, Arg.Elements[0].pVariable.CppName)
                CppText += IndentText + "%s[2] = (unsigned char) %s[2];\n" % (DestColorArray, Arg.Elements[0].pVariable.CppName)
            elif elem0type == ElemType.FUNC_CALL:
                my_temp = self.LogoState.TempIdx
                self.LogoState.TempIdx += 1
                codetext = self.GetCppInstruction(Arg.Elements[0].pInstruct, 0, False)
                if codetext is None:
                    return None
                CppText += IndentText + "CList<%s> templist%02i = %s;\n" % (self.LogoState.NumType, my_temp, codetext)
                CppText += IndentText + "%s[0] = (unsigned char) templist%02i[0];\n" % (DestColorArray, my_temp)
                CppText += IndentText + "%s[1] = (unsigned char) templist%02i[1];\n" % (DestColorArray, my_temp)
                CppText += IndentText + "%s[2] = (unsigned char) templist%02i[2];\n" % (DestColorArray, my_temp)
            else:
                print "Internal error: invalid element type %i '%s' in a List argument." % (elem0type, ElemType.Names[elem0type])
                return None
        else: # must be ParamType.NUMBER
            ArgText = self.GetCppArgument(Arg)
            if ArgText is None:
                return None
            if len(Arg.Elements) > 1:
                ArgText = "(" + ArgText + ")"
            CppText = IndentText + "*((int *)%s) = *((int *) tt_Colors[(int) (%s) & 15]);\n" % (DestColorArray, ArgText)
        return CppText

    def GetCppBuiltinJump(self, IndentText, UpdateTurtleText):
        NextIndent = IndentText + " " * self.IndentSize
        NumTypeGL = self.LogoState.NumType[0]
        CppText = ""
        # write code to draw the line
        if self.LogoState.bUseWrap:
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "%s NewPos[2];\n" % self.LogoState.NumType
            CppText += UpdateTurtleText.replace('tt_TurtlePos', 'NewPos')
            CppText += NextIndent + "wrapper_DrawLineSegment(tt_TurtlePos, NewPos, tt_UseWrap);\n"
            CppText += NextIndent + "tt_TurtlePos[0] = NewPos[0];\n" + NextIndent + "tt_TurtlePos[1] = NewPos[1];\n"
            CppText += IndentText + "} else {\n"
        else:
            CppText += IndentText + "if (tt_PenDown)\n" + IndentText + "{\n"
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeGL
            CppText += UpdateTurtleText
            CppText += NextIndent + "glVertex2%s(tt_TurtlePos[0], tt_TurtlePos[1]);\n" % NumTypeGL
            CppText += IndentText + "} else {\n"
        # write code for the PenUp case
        CppText += UpdateTurtleText
        CppText += IndentText + "}\n"
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
        NewXText = "tt_TurtlePos[0] %s sin%s(tt_TurtleDir*tt_RadDegree) * %s%s;\n" % (DirSign, NumTypeMath, ArgText, ScrunchText)
        # write expression to calculate the new Y position
        if self.LogoState.bUseScrunch:
            ScrunchText = " * tt_ScrunchXY[1]"
        NewYText = "tt_TurtlePos[1] %s cos%s(tt_TurtleDir*tt_RadDegree) * %s%s;\n" % (DirSign, NumTypeMath, ArgText, ScrunchText)
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


