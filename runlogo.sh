#!/bin/sh
name=`basename "$1"`
destdir=`dirname "$1"`
basename=${name%%.*}

if [ ! -f $1 ]; then
  echo "Input LOGO file $1 not found"
  exit 1
fi

includedir=`pwd`
cd "$destdir"

cppname=$basename.cpp
echo "Compiling $name to $cppname"
"$includedir"/turboturtle.py $name $cppname
if [ $? != 0 ]; then exit 2; fi

objname=$basename.o
echo "Compiling $cppname to $objname"
g++ -o $objname -O3 -I/usr/include/SDL -I"$includedir" -c $cppname
if [ $? != 0 ]; then exit 3; fi

echo "Compiling wrapper code"
g++ -o "$includedir"/wrapper.o -O3 -I/usr/include/SDL -I"$includedir" -c "$includedir"/wrapper_main.cpp
if [ $? != 0 ]; then exit 4; fi

exename="$includedir"/$basename
echo "Linking wrapper code with $objname to produce executable $exename."
g++ -o $exename -lSDL -lGL -lm $objname "$includedir"/wrapper.o

