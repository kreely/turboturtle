#==================================================
# tt_instruction.py - 2009-01-13
# The Instruction, Argument, and Element classes for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

class Element:
    def __init__(self, Type, Text, Instruction=None):
        self.Type = Type
        self.Text = Text
        self.pInstruct = Instruction
        self.pVariable = None

class Argument:
    def __init__(self):
        self.ArgType = ParamType.UNKNOWN
        self.Elements = []

    def ParseFromCodeElements(self, CodeElements, ProcName, Procedures):
        ErrProcName = ProcName or 'global'
        elemtype = CodeElements[0][0]
        # check for the easy ones first
        if elemtype == ElemType.QUOTED_WORD:
            elem = CodeElements.pop(0)
            self.ArgType = ParamType.QUOTEDWORD
            self.Elements.append(Element(ElemType.QUOTED_WORD, elem[1]))
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
                self.Elements.append(Element(elem[0], elem[1]))
                for ch in elem[1]:
                    if not (ch.isdigit() or ch == '.' or ch =='[' or ch == ']'):
                        self.ArgType = ParamType.LISTCODE
            # check bracket pairing
            if bracketDepth != 0:
                print "Syntax error: List ended with unclosed bracket in procedure '%s'" % ErrProcName
                return False
            # set elements to NUMBER type if this is a LISTNUM
            if self.ArgType == ParamType.LISTNUM:
                for elem in self.Elements:
                    elem.Type = ElemType.NUMBER
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
                        Instruct = Instruction(name, True, procs[0].nParams, True, procs[0].bExtraArgs)
                        if not Instruct.GetArguments(InstrElements, ProcName, Procedures):
                            return False
                        if len(InstrElements) > 0:
                            print "Syntax error: extraneous code in parenthesized instruction '%s' in procedure '%s'" % (name, ErrProcName)
                            return False
                        self.Elements.append(Element(ElemType.FUNC_CALL, name, Instruct))
                        bSpecialProc = True
                if not bSpecialProc:
                    # nope, just a regular old parenthesis
                    parenDepth += 1
                    self.Elements.append(Element(ElemType.OPEN_PAREN, elem[1]))
                    if len(CodeElements) == 0:
                        print "Syntax error: hanging open-parenthesis in procedure '%s'" % ErrProcName
                        return False
                    if CodeElements[0][0] == ElemType.CLOSE_PAREN:
                        print "Syntax error: empty parenthesis pair in procedure '%s'" % ErrProcName
                        return False
                    if CodeElements[0][0] == ElemType.QUOTED_WORD or CodeElements[0][0] == ElemType.INFIX_BOOL or (CodeElements[0][0] == ElemType.INFIX_NUM and CodeElements[0][1] != '-'):
                        print "Syntax error: invalid symbol '%s' after open-parenthesis in procedure '%s'" % (CodeElements[0][1], ErrProcName)
                        return False
                    continue
            elif elem[0] == ElemType.CLOSE_PAREN:
                if parenDepth == 0:
                    print "Syntax error: unmatched close-parenthesis in procedure '%s'" % ErrProcName
                    return False
                parenDepth -= 1
                self.Elements.append(Element(ElemType.CLOSE_PAREN, elem[1]))
            # handle a sub-procedure call
            elif elem[0] == ElemType.UNQUOT_WORD:
                # push the procedure name back on the element list and call the parser function
                CodeElements.insert(0, elem)
                Instruct = Parser.GetSingleInstruction(CodeElements, ProcName, Procedures)
                if Instruct is None:
                    return False
                self.Elements.append(Element(ElemType.FUNC_CALL, elem[1], Instruct))
            # handle values
            elif elem[0] == ElemType.NUMBER or elem[0] == ElemType.BOOLEAN or elem[0] == ElemType.VAR_VALUE:
                self.Elements.append(Element(elem[0], elem[1]))
            # handle infix operators
            elif elem[0] == ElemType.INFIX_NUM or elem[0] == ElemType.INFIX_BOOL:
                self.Elements.append(Element(elem[0], elem[1]))
                if len(CodeElements) == 0:
                    print "Syntax error: hanging infix '%s' in expression in procedure '%s'" % (elem[1], ErrProcName)
                    return False
                if CodeElements[0][0] == ElemType.CLOSE_PAREN:
                    print "Syntax error: missing value between '%s' and '%s' in procedure '%s'" % (elem[1], CodeElements[0][1], ErrProcName)
                    return False
                if CodeElements[0][0] == ElemType.QUOTED_WORD or CodeElements[0][0] == ElemType.INFIX_BOOL or (CodeElements[0][0] == ElemType.INFIX_NUM and CodeElements[0][1] != '-'):
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

    # this is a function which retrieves a ParamType for a list of elements (an expression)
    # this function should only be called starting from an Elements list of an Argument of type ParamType.UNKNOWN
    # Arguments with types LISTCODE, LISTNUM, and QUOTEDWORD should have been parsed earlier, so we don't worry about them
    # Note: this function destroys the list which is passed in
    @staticmethod
    def GetExpressionType(ElemList):
        # sanity check
        if len(ElemList) == 0:
            print "Internal error: empty list in GetExpressionType call"
            return ParamType.NOTHING
        # first, if any FUNC_CALL or VAL_TYPE elements are typed UNKNOWN, then we can't get the value of this expression
        for elem in ElemList:
            if elem.Type == ElemType.VAR_VALUE and (elem.pVariable is None or elem.pVariable.Type == ParamType.UNKNOWN):
                return ParamType.UNKNOWN
            elif elem.Type == ElemType.FUNC_CALL and (elem.pInstruct.pProc is None or elem.pInstruct.pProc.ReturnType == ParamType.UNKNOWN):
                return ParamType.UNKNOWN
        # otherwise, assume it's an expression and parse the elements in order
        bNumericExpression = False
        while (len(ElemList) > 0):
            # at the start of this loop, we're looking for a value (NUMBER, BOOLEAN, OPEN_PAREN, VAR_VALUE, or FUNC_CALL)
            elem = ElemList.pop(0)
            valtype = ParamType.UNKNOWN
            bNegValue = False
            # first, check for negative sign
            if elem.Type == ElemType.INFIX_NUM and elem.Text == '-' and len(ElemList) > 0 and (valtype == ParamType.UNKNOWN or valtype == ParamType.NUMBER):
                bNegValue = True
                elem = ElemList.pop(0)
            # look for a value
            if elem.Type == ElemType.OPEN_PAREN:
                # retrieve the value for this parenthesized sub-expression
                depth = 1
                subelemlist = []
                while (depth > 0):
                    elem = ElemList.pop(0)
                    if elem.Type == ElemType.OPEN_PAREN:
                        depth += 1
                    elif elem.Type == ElemType.CLOSE_PAREN:
                        depth -= 1
                    if depth > 0:
                        subelemlist.append(elem)
                valtype = Argument.GetExpressionType(subelemlist)
                if valtype is None:
                    return None
            elif elem.Type == ElemType.NUMBER:
                valtype = ParamType.NUMBER
            elif elem.Type == ElemType.BOOLEAN:
                valtype = ParamType.BOOLEAN
            elif elem.Type == ElemType.VAR_VALUE:
                valtype = elem.pVariable.Type
            elif elem.Type == ElemType.FUNC_CALL:
                valtype = elem.pInstruct.pProc.ReturnType
            else:
                print "Syntax error: unexpected element '%s' type %i in expression" % (elem.Text, elem.Type)
                return None
            # check for a syntax error with negating a non-numeric value
            if bNegValue and valtype != ParamType.NUMBER:
                print "Syntax error: negative sign cannot be used on value of type '%s' in expression" % ParamType.Names[valtype]
                return None
            # check for syntax errors with non-numeric and/or non-boolean values inside of an expression
            if bNumericExpression is True and valtype != ParamType.NUMBER:
                print "Syntax error: non-numeric value (type '%s') inside a numeric expression" % ParamType.Names[valtype]
                return None
            if valtype != ParamType.NUMBER and valtype != ParamType.BOOLEAN and len(ElemList) > 0:
                clausetext = " ".join([elem.Text for elem in ElemList])
                print "Syntax error: extraneous clause '%s' following non-numeric and non-boolean value (type '%s') in expression" % (clausetext, ParamType.Names[valtype])
                return None
            # otherwise, if value type is non-numeric and non-boolean then it's a singleton and it's okay, so return the type
            if valtype != ParamType.NUMBER and valtype != ParamType.BOOLEAN:
                return valtype
            # also, if there are no more elements, then the expression is okay and the type is in valtype
            if len(ElemList) == 0:
                return valtype
            # now, there are remaining elements in the list and the expression is either a boolean or a numeric one
            infixelem = ElemList.pop(0)
            if infixelem.Type == ElemType.INFIX_BOOL:
                # boolean is a special case: the remainder of the expression must evaluate to the same type as the valtype
                if bNumericExpression is True:
                    print "Syntax error: invalid boolean operator '%s' following a numeric value in an expression" % infixelem.Text
                    return None
                if len(ElemList) == 0:
                    print "Syntax error: hanging boolean operator '%s' in expression" % infixelem.Text
                    return None
                rtype = Argument.GetExpressionType(ElemList)
                if rtype is None:
                    return None
                if rtype != valtype:  # either bool/bool or num/num comparisons are allowed
                    print "Syntax error: values of type %s and %s being compared to each other" % (ParamType.Names[valtype], ParamType.Names[rtype])
                    return None
                if rtype == ParamType.BOOLEAN and infixelem.Text != '=' and infixelem.Text != '<>':
                    print "Syntax error: invalid operator '%s' used on boolean values" % infixelem.Text
                    return None
                # it's a good boolean expression
                return ParamType.BOOLEAN
            elif infixelem.Type == ElemType.INFIX_NUM:
                if valtype == ParamType.BOOLEAN:
                    print "Syntax error: invalid numeric operator '%s' following a boolean value in an expression" % infixelem.Text
                    return None
                if len(ElemList) == 0:
                    print "Syntax error: hanging numeric operator '%s' in expression" % infixelem.Text
                    return None
                # fall through to get another value in the numeric expression
                bNumericExpression = True
            else:
                print "Syntax error: invalid element '%s' type '%s' following a %s value in an expression" % (infixelem.Text, ElemType.Names[infixelem.Type], ParamType.Names[valtype])
                return None
            # go pull out the next value, only a numeric expression can reach here
        # if we fall out of the loop above, it's an error (probably an internal error because previous checks should prevent this)
        print "Internal error: extraneous operators or missing values in %s expression" % {False:"boolean",True:"numeric"}[bNumericExpression]
        return None

class Instruction:
    def __init__(self, Name, BuiltIn, nParams, bParenthesized, bExtraArgs):
        self.Name = Name
        self.BuiltIn = BuiltIn
        self.pProc = None
        self.pMakeVar = None
        self.nParams = nParams
        self.bParenthesized = bParenthesized
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

# the imports are at the bottom of this file to get around a python problem caused by
# an unavoidable circular dependency among the Parser, Instruction, and Argument classes
from tt_types import *
from tt_parser import *

