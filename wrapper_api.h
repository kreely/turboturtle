
/********************************************/
/* Turbo Turtle Logo Core/Wrapper Interface */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

// Functions and data in the compiled Logo C++ file
void tt_LogoMain(void);
extern unsigned char tt_ColorPen[];
extern unsigned char tt_ColorBackground[];

// Functions in the OpenGL wrapper
void wrapper_Clean(void);
void wrapper_DrawLineSegment(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled);
void wrapper_DrawLineSegment(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled);

