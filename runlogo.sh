#!/bin/sh
name=`basename "$1"`
destdir=`dirname "$1"`
basename=${name%%.*}

if [ ! -f $1 ]; then
  echo "Input LOGO file $1 not found"
  exit 1
fi

includedir=`pwd`

cppname=$basename.cpp
echo "Compiling $name to $cppname"
"$includedir"/turboturtle.py "$destdir"/$name "$destdir"/$cppname
if [ $? != 0 ]; then exit 2; fi

objname=$basename.o
echo "Compiling $cppname to $objname"
g++ -o "$destdir"/$objname -O3 -I/usr/include/SDL -I. -c "$destdir"/$cppname
if [ $? != 0 ]; then exit 3; fi

echo "Compiling wrapper code"
g++ -o wrapper_main.o -O3 -I/usr/include/SDL -I. -c wrapper_main.cpp
if [ $? != 0 ]; then exit 4; fi
g++ -o wrapper_opengl.o -O3 -I/usr/include/SDL -I. -c wrapper_opengl.cpp
if [ $? != 0 ]; then exit 4; fi
g++ -o wrapper_pointtext.o -O3 -I/usr/include/SDL -I. -c wrapper_pointtext.cpp
if [ $? != 0 ]; then exit 4; fi
g++ -o wrapper_fontdata.o -O3 -c wrapper_fontdata.cpp
if [ $? != 0 ]; then exit 4; fi

echo "Linking wrapper code with $objname to produce executable $basename."
g++ -o $basename -lSDL -lGL -lm "$destdir"/$objname wrapper_main.o wrapper_opengl.o wrapper_fontdata.o wrapper_pointtext.o

