#==================================================
# tt_instruction.py - 2009-01-13
# The Instruction and Argument classes for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_types import *
from tt_parser import *

class Argument:
    def __init__(self):
        self.ArgType = ParamType.UNKNOWN
        self.nElem     = 0
        self.ElemTypes = []
        self.ElemText  = []
        self.ElemInstr = []
        
    def AddElement(self, ElemType, Text, Instruction):
        self.nElem += 1
        self.ElemTypes.append(ElemType)
        self.ElemText.append(Text)
        self.ElemInstr.append(Instruction)

    def ParseFromCodeElements(self, CodeElements, ProcName, Procedures):
        ErrProcName = ProcName or 'global'
        elemtype = CodeElements[0][0]
        # check for the easy ones first
        if elemtype == ElemType.QUOTED_WORD:
            elem = CodeElements.pop(0)
            self.ArgType = ParamType.QUOTEDWORD
            self.AddElement(ElemType.QUOTED_WORD, elem[1], None)
            return True
        elif elemtype == ElemType.OPEN_BRACKET:
            CodeElements.pop(0)
            bracketDepth = 1
            # assume that it's a numeric list at the start, and if any non-numbers are found then we'll call it a code list instead
            self.ArgType = ParamType.LISTNUM
            while len(CodeElements) > 0:
                elem = CodeElements.pop(0)
                if elem[0] == ElemType.OPEN_BRACKET:
                    bracketDepth += 1
                if elem[0] == ElemType.CLOSE_BRACKET:
                    bracketDepth -= 1
                    if bracketDepth == 0:
                        break
                self.AddElement(elem[0], elem[1], None)
                for ch in elem[1]:
                    if not (ch.isdigit() or ch == '.' or ch =='[' or ch == ']'):
                        self.ArgType = ParamType.LISTCODE
            if bracketDepth != 0:
                print "Syntax error: List ended with unclosed bracket in procedure '%s'" % ErrProcName
                return False
            return True
        # otherwise, assume that we are parsing either a boolean or numeric expression
        parenDepth = 0
        while len(CodeElements) > 0:
            elem = CodeElements.pop(0)
            if elem[0] == ElemType.OPEN_BRACKET or elem[0] == ElemType.CLOSE_BRACKET:
                print "Syntax error: invalid bracket '%s' found in expression in procedure '%s'" % (elem[1], ErrProcName)
                return False
            elif elem[0] == ElemType.OPEN_PAREN:
                # check for parenthesized built-in procedure calls
                bSpecialProc = False
                if CodeElements[0][0] == ElemType.UNQUOT_WORD:
                    name = CodeElements[0][1]
                    procs = [ proc for proc in Builtin._procs if proc.bParenthesized and (proc.FullName == name.lower() or proc.AbbrevName == name.lower()) ]
                    if len(procs) > 0:
                        # okay, we're looking at a special instruction form
                        # first, extract a code element stream for only this instruction
                        InstrElements = []
                        InstrParen = 1
                        while len(CodeElements) > 0:
                            elem = CodeElements.pop(0)
                            if elem[0] == ElemType.OPEN_PAREN:
                                InstrParen += 1
                            elif elem[0] == ElemType.CLOSE_PAREN:
                                InstrParen -= 1
                                if InstrParen == 0:
                                    break
                            InstrElements.append(elem)
                        # now, create the special instruction and check that all elements were used
                        Instruct = Instruction(name, True, procs[0].nParams, procs[0].bExtraNumbers)
                        if not Instruct.GetArguments(InstrElements, ProcName, Procedures):
                            return False
                        if len(InstrElements) > 0:
                            print "Syntax error: extraneous code in parenthesized instruction '%s' in procedure '%s'" % (name, ErrProcName)
                            return False
                        self.AddElement(ElemType.FUNC_CALL, name, Instruct)
                        bSpecialProc = True
                if not bSpecialProc:
                    # nope, just a regular old parenthesis
                    parenDepth += 1
                    self.AddElement(ElemType.OPEN_PAREN, elem[1], None)
                    if len(CodeElements) == 0:
                        print "Syntax error: hanging open-parenthesis in procedure '%s'" % ErrProcName
                        return False
                    if CodeElements[0][0] == ElemType.CLOSE_PAREN:
                        print "Syntax error: empty parenthesis pair in procedure '%s'" % ErrProcName
                        return False
                    if CodeElements[0][0] == ElemType.QUOTED_WORD or CodeElements[0][0] == ElemType.INFIX_BOOL or CodeElements[0][0] == ElemType.INFIX_NUM:
                        print "Syntax error: invalid symbol '%s' after open-parenthesis in procedure '%s'" % (CodeElements[0][1], ErrProcName)
                        return False
                    continue
            elif elem[0] == ElemType.CLOSE_PAREN:
                if parenDepth == 0:
                    print "Syntax error: unmatched close-parenthesis in procedure '%s'" % ErrProcName
                    return False
                parenDepth -= 1
                self.AddElement(ElemType.CLOSE_PAREN, elem[1], None)
            # handle a sub-procedure call
            elif elem[0] == ElemType.UNQUOT_WORD:
                # push the procedure name back on the element list and call the parser function
                CodeElements.insert(0, elem)
                Instruct = Parser.GetSingleInstruction(CodeElements, ProcName, Procedures)
                if Instruct is None:
                    return False
                self.AddElement(ElemType.FUNC_CALL, elem[1], Instruct)
            # handle values
            elif elem[0] == ElemType.NUMBER or elem[0] == ElemType.BOOLEAN or elem[0] == ElemType.VAR_VALUE:
                self.AddElement(elem[0], elem[1], None)
            # handle infix operators
            elif elem[0] == ElemType.INFIX_NUM or elem[0] == ElemType.INFIX_BOOL:
                self.AddElement(elem[0], elem[1], None)
                if len(CodeElements) == 0:
                    print "Syntax error: hanging infix '%s' in expression in procedure '%s'" % (elem[1], ErrProcName)
                    return False
                if CodeElements[0][0] == ElemType.CLOSE_PAREN:
                    print "Syntax error: missing value between '%s' and '%s' in procedure '%s'" % (elem[1], CodeElements[0][1], ErrProcName)
                    return False
                if CodeElements[0][0] == ElemType.QUOTED_WORD or CodeElements[0][0] == ElemType.INFIX_BOOL or CodeElements[0][0] == ElemType.INFIX_NUM:
                    print "Syntax error: invalid symbol '%s' after operator '%s' in procedure '%s'" % (CodeElements[0][1], elem[1], ErrProcName)
                    return False
                continue
            # unknown element type or bug
            else:
                print "Syntax error: unknown element code %i in text '%s' from procedure '%s'" % (int(elem[0]), elem[1], ErrProcName)
                return False
            if len(CodeElements) == 0:
                break
            if CodeElements[0][0] == ElemType.CLOSE_PAREN and parenDepth > 0:
                continue
            if CodeElements[0][0] != ElemType.INFIX_BOOL and CodeElements[0][0] != ElemType.INFIX_NUM:
                break
        # check parenthesis depth
        if parenDepth != 0:
            print "Syntax error: Expression ended with unclosed parenthesis in procedure '%s'.  Missing operator or closing parenthesis?" % ErrProcName
            return False
        return True

class Instruction:
    def __init__(self, Name, BuiltIn, nParams, bExtraArgs):
        self.Name = Name
        self.BuiltIn = BuiltIn
        self.nParams = nParams
        self.bExtraArgs = bExtraArgs
        self.Arguments = [ ]

    def GetArguments(self, CodeElements, ProcName, Procedures):
        if self.bExtraArgs:
            # we don't know how many arguments will be given, so just take everything available
            self.nParams = 0
            while len(CodeElements) > 0:
                newarg = Argument()
                if not newarg.ParseFromCodeElements(CodeElements, ProcName, Procedures):
                    return False
                self.Arguments.append(newarg)
                self.nParams += 1
            return True
        # we do know how many arguments will be given to this instruction, so only take that many
        for i in range(self.nParams):
            newarg = Argument()
            if not newarg.ParseFromCodeElements(CodeElements, ProcName, Procedures):
                return False
            self.Arguments.append(newarg)
        return True


