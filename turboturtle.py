#!/usr/bin/env python
#==================================================
# TurboTurtle.py - 2009-01-13
# A Logo to C++ translator for fast Turtle Graphics
# Copyright (c) 2009 by Richard Goedeken
#--------------------------------------------------

import os, sys
from tt_parser import *

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
        # the second pass extracts the defined procedures
        (self.MainCode, self.Procedures) = Parser.ExtractProcedures(self.InputCode)
        if self.MainCode == None or self.Procedures == None:
            return
        # fixme debug
        print "Main Code: %s" % self.MainCode
        for proc in self.Procedures:
            print "Procedure '%s':" % proc.Name
            print "    Inputs: %s" % ",".join([var.Name for var in proc.InputVariables])
            print "    Code: %s" % proc.CodeText

# this function is executed when this script is run (not imported)
if __name__ == '__main__':
    # run the main function at the top of this source file
    main()
