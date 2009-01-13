#==================================================
# tt_parser.py - 2009-01-13
# The Parser class for Turbo Turtle
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

from tt_procedure import *
from tt_variable import *

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

