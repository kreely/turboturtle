#==================================================
# tt_parser.py - 2009-01-13
# The Parser class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

class Parser:
    def __init__(self):
        pass

    @staticmethod
    def RemoveCommentsContinueLines(InText):
        OutText = ""
        for line in InText.split('\n'):
            # remove carriage returns
            line = line.replace('\r', '')
            if len(line) == 0:
                continue
            # check for presence of continuation character
            bContinue = False
            if line[-1] == '~':
                bContinue = True
                line = line[:-1]
            # remove any comments
            i = line.find(";")
            if i >= 0:
                line = line[:i]
            # add this line to the output text
            if bContinue:
                OutText += line
            else:
                OutText += line + '\n'
        return OutText

    @staticmethod
    def ExtractProcedures(InText):
        MainCode = ""
        Procedures = []
        # iterate through the lines of source code, stick the code together, and pull out the defined procedures
        CurCode = ""
        CurProc = None
        for line in InText.split('\n'):
            # remove any leading or trailing whitespace
            line = line.strip()
            # break it into words
            words = line.split()
            if len(words) == 0:
                continue
            # see if this is the start of a procedure
            if words[0].lower() == "to":
                # check if we are already in a procedure definition
                if CurProc is not None:
                    print "Syntax error: illegal TO instruction inside procedure definition for \"%s\"" % CurProc.Name
                    return (None, None)
                # get the procedure and variable names
                procname = words[1]
                varnames = []
                for name in words[2:]:
                    if len(name) < 2:
                        print "Syntax error: invalid parameter name \"%s\" for procedure \"%s\"" % (name, procname)
                        return (None, None)
                    if name[0] != ':':
                        print "Syntax error: missing dots in parameter \"%s\" name for procedure \"%s\"" % (name, procname)
                        return (None, None)
                    varnames.append(name[1:])
                # check for invalid procedure name
                if procname.lower() == 'to' or procname.lower() == 'end' or procname.lower() == 'true' or procname.lower() == 'false':
                    print "Syntax error: invalid procedure name: protected word '%s'" % procname
                    return (None, None)
                # check for built-in function with same name
                duplist = [proc for proc in Builtin._procs if proc.FullName == procname.lower() or proc.AbbrevName == procname.lower() ]
                if len(duplist) > 0:
                    print "Syntax error: procedure '%s' name is duplicate of built-in procedure" % procname
                    return (None, None)
                # check for duplicate definition
                duplist = [proc for proc in Procedures if proc.Name.lower() == procname.lower()]
                if len(duplist) > 0:
                    print "Syntax error: duplicate definition for procedure \"%s\"" % procname
                    return (None, None)
                # create the new procedure
                CurProc = Procedure(procname, varnames)
                CurCode = ""
                continue
            # see if this is the end of a procedure
            if words[0].lower() == "end":
                # check for extra code
                if len(words) > 1:
                    print "Syntax error: extraneous code \"%s\" after END" % " ".join(words[1:])
                    return (None, None)
                # make sure that we're actually in a procedure definition
                if CurProc is None:
                    print "Syntax error: END instruction outside of procedure definition"
                    return (None, None)
                # add this procedure to the list and continue
                CurProc.AddCode(CurCode)
                Procedures.append(CurProc)
                CurProc = None
                continue
            # this is a normal code line, so add it somewhere
            if CurProc is None:
                if MainCode == "":
                    MainCode = line
                else:
                    MainCode += " " + line
            else:
                if CurCode == "":
                    CurCode = line
                else:
                    CurCode += " " + line
            # continue with line processing
        # check for un-terminated procedure
        if CurProc is not None:
            print "Syntax error: No END found for procedure \"%s\"" % CurProc.Name
            return (None, None)
        return (MainCode, Procedures)

    @staticmethod
    def ParseStreamElements(CodeText, ProcName):
        ErrProcName = ProcName or 'global'
        Elements = []
        bracketDepth = 0
        bFirst = True
        while len(CodeText) > 0:
            bPriorSpace = False
            if CodeText[0] == ' ' or bFirst:
                bFirst = False
                bPriorSpace = True
            CodeText = CodeText.strip()
            elemtext = CodeText[0]
            CodeText = CodeText[1:]
            # first, parse any open or closing brackets
            if elemtext == '[':
                Elements.append((ElemType.OPEN_BRACKET, elemtext))
                bracketDepth += 1
                continue
            elif elemtext == ']':
                if bracketDepth <= 0:
                    print "Syntax error: unmatched closing bracket ']' in procedure '%s'" % ErrProcName
                    return None
                Elements.append((ElemType.CLOSE_BRACKET, elemtext))
                bracketDepth -= 1
                continue
            # Next, only tokenize the other elements if we are _not_ inside of a list (brackets)
            if bracketDepth == 0:
                if elemtext == '(':
                    Elements.append((ElemType.OPEN_PAREN, elemtext))
                    continue
                elif elemtext == ')':
                    Elements.append((ElemType.CLOSE_PAREN, elemtext))
                    continue
                elif elemtext in '+*/' or (elemtext == '-' and (CodeText[0] not in '0123456789' or not bPriorSpace)):
                    Elements.append((ElemType.INFIX_NUM, elemtext))
                    continue
                elif elemtext in '<=>':
                    if (elemtext == '<' and (CodeText[0] in ('=', '>'))) or (elemtext == '>' and CodeText[0] == '='):
                        elemtext = elemtext + CodeText[0]
                        CodeText = CodeText[1:]
                    Elements.append((ElemType.INFIX_BOOL, elemtext))
                    continue
                elif elemtext == '"':
                    elemtype = ElemType.QUOTED_WORD
                elif elemtext == ':':
                    elemtype = ElemType.VAR_VALUE
                else:
                    elemtype = ElemType.UNQUOT_WORD
            else:
                # we are inside of a list, so everything is a word
                elemtype = ElemType.UNQUOT_WORD
            # determine the separators and scoop up this element
            if bracketDepth != 0:
                dividers = ' []'
            elif elemtype == ElemType.QUOTED_WORD:
                dividers = ' []()'
            else:
                dividers = ' []()+-*/<=>'
            while len(CodeText) > 0 and CodeText[0] not in dividers:
                elemtext = elemtext + CodeText[0]
                CodeText = CodeText[1:]
            if elemtype == ElemType.UNQUOT_WORD and bracketDepth == 0:
                # check for numbers
                if elemtext[0] in '-0123456789' and len([ch for ch in elemtext[1:] if ch not in '0123456789.']) == 0:
                    elemtype = ElemType.NUMBER
                # check for immediate booleans
                elif elemtext.lower() == "true" or elemtext.lower() == "false":
                    elemtype = ElemType.BOOLEAN
            # check for invalid elements
            if elemtext == '"':
                print "Syntax error: emtpy quotation mark in procedure '%s'" % ErrProcName
                return None
            if elemtext == ':':
                print "Syntax error: emtpy dots in procedure '%s'" % ErrProcName
                return None
            # everything's good, add this element to the list
            Elements.append((elemtype, elemtext))
        if bracketDepth != 0:
            print "Syntax error: unmatched [] brackets in procedure '%s'" % ErrProcName
            return None
        return Elements

    @staticmethod
    def GetSingleInstruction(CodeElements, ProcName, Procedures):
        ErrProcName = ProcName or 'global'
        firstelem = CodeElements.pop(0)
        # first, handle parenthesized BuiltIn instructions
        if firstelem[0] == ElemType.OPEN_PAREN:
            if CodeElements[0][0] != ElemType.UNQUOT_WORD:
                print "Syntax error in '%s': Invalid instruction starting with '(%s'" % (ErrProcName, CodeElements[0][1])
                return None
            name = CodeElements.pop(0)[1]
            procs = [ proc for proc in Builtin._procs if proc.bParenthesized and (proc.FullName == name.lower() or proc.AbbrevName == name.lower()) ]
            if len(procs) == 0:
                print "Syntax error in '%s': Invalid parenthesized instruction '%s'" % (ErrProcName, name)
                return None
            # extract a code element stream for only this instruction
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
            return Instruct
        # otherwise it must be a normal (un-parenthesized) instruction
        if firstelem[0] != ElemType.UNQUOT_WORD:
            print "Syntax error in '%s': Found invalid word '%s' instead of an Instruction" % (ErrProcName, firstelem[1])
            return None
        InstructName = firstelem[1]
        # Search for a procedure with this name
        builtinlist = [ proc for proc in Builtin._procs if proc.FullName == InstructName.lower() or proc.AbbrevName == InstructName.lower() ]
        if len(builtinlist) > 0:
            Instruct = Instruction(InstructName, True, builtinlist[0].nParams, False, False)
            if not Instruct.GetArguments(CodeElements, ProcName, Procedures):
                return None
        else:
            proclist = [ proc for proc in Procedures if proc.Name.lower() == InstructName.lower() ]
            if len(proclist) > 0:
                Instruct = Instruction(InstructName, False, len(proclist[0].InputVariables), False, False)
                if not Instruct.GetArguments(CodeElements, ProcName, Procedures):
                    return None
            else:
                print "Syntax error: invalid instruction named '%s' found while parsing '%s'" % (InstructName, ErrProcName)
                return None
        return Instruct

# the imports are at the bottom of this file to get around a python problem caused by
# an unavoidable circular dependency among the Parser, Instruction, and Argument classes
from tt_procedure import *
from tt_instruction import *
from tt_builtin import *
from tt_types import *

