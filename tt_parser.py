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
            Instructions.append(instruction)
        return Instructions

    @staticmethod
    def ParseStreamElements(CodeText, ProcName):
        Elements = []
        inBracket = False
        while len(CodeText) > 0:
            CodeText = CodeText.strip()
            elemtext = CodeText[0]
            CodeText = CodeText[1:]
            if elemtext == '[':
                Elements.append((ElemType.OPEN_BRACKET, elemtext))
                inBracket = True
                continue
            elif elemtext == ']':
                Elements.append((ElemType.CLOSE_BRACKET, elemtext))
                inBracket = False
                continue
            elif elemtext == '(':
                Elements.append((ElemType.OPEN_PAREN, elemtext))
                continue
            elif elemtext == ')':
                Elements.append((ElemType.CLOSE_PAREN, elemtext))
                continue
            elif elemtext in '+-*/' and not inBracket:
                Elements.append((ElemType.INFIX_NUM, elemtext))
                continue
            elif elemtext in '<=>' and not inBracket:
                if (elemtext == '<' and (CodeText[0] == '=' or CodeText[0] == '>')) or (elemtext == '>' and CodeText[0] == '='):
                    elemtext = elemtext + CodeText[0]
                    CodeText = CodeText[1:]
                Elements.append((ElemType.INFIX_BOOL, elemtext))
                continue
            elif elemtext == '"':
                elemtype = ElemType.QUOTED_WORD
            elif elemtext == ':':
                elemtype = ElemType.VAR_VALUE
            elif elemtext in '0123456789':
                elemtype = ElemType.NUMBER
            else:
                elemtype = ElemType.UNQUOT_WORD
            # determine the separators and scoop up this element
            if inBracket:
                dividers = ' ]'
            elif elemtype == ElemType.QUOTED_WORD:
                dividers = ' []()'
            else:
                dividers = ' []()+-*/<=>'
            while len(CodeText) > 0 and CodeText[0] not in dividers:
                elemtext = elemtext + CodeText[0]
                CodeText = CodeText[1:]
            # check for immediate booleans
            if elemtype == ElemType.UNQUOT_WORD and (elemtext.lower() == "true" or elemtext.lower() == "false"):
                elemtype == ElemType.BOOLEAN
            # check for invalid elements
            if elemtext == '"':
                print "Syntax error: emtpy quotation mark in procedure '%s'" % ProcName
                return
            if elemtext == ':':
                print "Syntax error: emtpy dots in procedure '%s'" % ProcName
                return
            # everything's good, add this element to the list
            Elements.append((elemtype, elemtext))
        if inBracket:
            print "Syntax error: unmatched [] bracket in procedure '%s'" % ProcName
            return None
        return Elements

    @staticmethod
    def GetSingleInstruction(CodeElements, ProcName, Procedures):
        # look for invalid characters
        firstelem = CodeElements.pop(0)
        if firstelem[0] != ElemType.UNQUOT_WORD:
            print "Syntax error in '%s': Found invalid word '%s' instead of procedure call" % (ProcName, firstelem[1])
            return None
        InstructName = firstelem[1]
        # Search for a procedure with this name
        builtinlist = [ proc for proc in Builtin._procs if proc.FullName == InstructName.lower() or proc.AbbrevName == InstructName.lower() ]
        if len(builtinlist) > 0:
            Instruct = Instruction(InstructName, True, builtinlist[0].nParams, False)
            if not Instruct.GetArguments(CodeElements, ProcName, Procedures):
                return None
        else:
            proclist = [ proc for proc in Procedures if proc.Name.lower() == InstructName.lower() ]
            if len(proclist) > 0:
                Instruct = Instruction(InstructName, False, len(proclist[0].InputVariables), False)
                if not Instruct.GetArguments(CodeElements, ProcName, Procedures):
                    return None
            else:
                print "Syntax error: invalid instruction named '%s' found while parsing '%s'" % (InstructName, ProcName)
                return None
        return Instruct

# the imports are at the bottom of this file to get around a python problem caused by
# an unavoidable circular dependency among the Parser, Instruction, and Argument classes
from tt_procedure import *
from tt_instruction import *
from tt_builtin import *
from tt_types import *


