
/********************************************/
/* Turbo Turtle Logo Core/Wrapper Interface */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

// Functions and data in the compiled Logo C++ file
void tt_LogoMain(void);
extern float          tt_FramesPerSec;
extern int            tt_WindowSize;
extern int            tt_LineSmooth;
extern unsigned char *tt_ActiveColor;
extern unsigned char  tt_ColorPen[];
extern unsigned char  tt_ColorBackground[];

// Functions in the Main wrapper
void wrapper_Clean(void);
void wrapper_Erase(void);

// Functions in the OpenGL wrapper
void wrapper_glFlushVertices(void);
void wrapper_glLineVertex(float fVertexX, float fVertexY);
void wrapper_glPointVertex(float fVertexX, float fVertexY);
void wrapper_glDrawLineWrap(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled);
void wrapper_glDrawLineWrap(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled);

