/********************************************/
/* Turbo Turtle Logo Core/Wrapper Interface */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/*     Richard@fascinationsoftware.com      */
/********************************************/

//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation, version 3.

//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.

//   You should have received a copy of the GNU General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.

// Functions and data in the compiled Logo C++ file
void tt_LogoMain(void);
extern float          tt_FramesPerSec;
extern int            tt_WindowSize;
extern int            tt_LineSmooth;
extern unsigned char *tt_ActiveColor;
extern unsigned char  tt_ColorPen[];
extern unsigned char  tt_ColorBackground[];

// Global data defined in the OpenGL wrapper
extern float fPixelsPerTurtleStep;
extern int   iScreenWidth;
extern int   iScreenHeight;
extern int   iViewWidth;
extern int   iViewHeight;

// Functions in the OpenGL wrapper
void wrapper_Clean(void);
void wrapper_Erase(void);
void wrapper_glFlushVertices(void);
void wrapper_glLineVertex(float fVertexX, float fVertexY);
void wrapper_glPointVertex(float fVertexX, float fVertexY);
void wrapper_glDrawLineWrap(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled);
void wrapper_glDrawLineWrap(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled);

