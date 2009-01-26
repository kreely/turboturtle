#!/bin/sh
name=`basename $1`
basename=${name%%.*}

if [ ! -f $1 ]; then
  echo "Input LOGO file $1 not found"
  exit 1
fi

cppname=$basename.cpp
echo "Compiling $1 to $cppname"
./turboturtle.py $1 $cppname
if [ $? != 0 ]; then exit 2; fi

objname=$basename.o
echo "Compiling $cppname to $objname"
g++ -o $objname -O3 -I/usr/include/SDL -c $cppname
if [ $? != 0 ]; then exit 3; fi

echo "Compiling wrapper code"
g++ -o wrapper.o -O3 -I/usr/include/SDL -c wrapper_main.cpp
if [ $? != 0 ]; then exit 4; fi

exename=$basename
echo "Linking wrapper code with $objname to produce executable."
g++ -o $exename -lSDL -lGL $objname wrapper.o

