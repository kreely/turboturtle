
/********************************************/
/* Turbo Turtle Logo Core/Wrapper Interface */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

// Functions and data in the compiled Logo C++ file
void tt_LogoMain(void);

// Functions in the OpenGL wrapper
void wrapper_SetBackground(int iR, int iG, int iB);
void wrapper_SetPenColor(int iR, int iG, int iB);
void wrapper_SetPenPaint(bool bPaint);
void wrapper_SetPenSize(float fSize);
void wrapper_SetPenSize(double dSize);

