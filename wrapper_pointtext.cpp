/**********************************************/
/* Turbo Turtle Wrapper - Point Text Renderer */
/*                                            */
/*  Copyright (c) 2009 by Richard Goedeken    */
/**********************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <SDL.h>
#include <SDL_opengl.h>

// these data are defined in wrapper_fontdata.cpp
extern const short bitmap_font10x18[96][18];
extern const short bitmap_font12x16[96][16];
extern const short bitmap_font8x12[96][12];

// these data are define in wrapper_main.cpp
extern float fPixelsPerTurtleStep;

struct font {
  const short *psBitmapData;
  int nFirstChar;
  int nChars;
  int nCols;
  int nRows;
  };

#define NUM_FONTS 3
struct font my_fonts[NUM_FONTS] = { { (const short *) bitmap_font8x12,  32, 96,  8, 12 },
                                    { (const short *) bitmap_font10x18, 32, 96, 10, 18 }, 
                                    { (const short *) bitmap_font12x16, 32, 96, 12, 16 } };

bool DrawPointText(int iFont, int iJustifyVert, int iJustifyHorz, float fHeight, float fX, float fY, const char *string)
{
    // return if font index is invalid
    if (iFont < 0 || iFont > NUM_FONTS - 1)
        return false;

    // get parameters for this font
    int iFirstChar = my_fonts[iFont].nFirstChar;
    int iFontChars = my_fonts[iFont].nChars;
    int iFontRows = my_fonts[iFont].nRows;
    int iFontCols = my_fonts[iFont].nCols;
    int iStrLength = strlen(string);

    // handle vertical justification
    float fTopY = fY;
    if (iJustifyVert == 1) fTopY += fHeight / 2.0;
    else if (iJustifyVert >= 2) fTopY += fHeight;

    // handle horizontal justification
    float fLeftX = fX;
    float fPointSpace = fHeight / iFontRows;
    if (iJustifyHorz == 1) fLeftX -= iStrLength * iFontCols * fPointSpace / 2.0;
    else if (iJustifyHorz >= 2) fLeftX -= iStrLength * iFontCols * fPointSpace;

    // set up openGL
    glEnable(GL_POINT_SMOOTH);
    glPointSize(fPointSpace * fPixelsPerTurtleStep * 1.5);
    glBegin(GL_POINTS);

    // dot-matrix it up
    for (int i = 0; i < iStrLength; i++)
    {
        char ch = string[i];
        if (ch >= iFirstChar && ch < iFirstChar + iFontChars)
        {
            const short *psLetterBitmap = my_fonts[iFont].psBitmapData + ((ch - iFirstChar) * iFontRows);
            for (int j = 0; j < iFontRows; j++)
            {
                int iRowBitmap = psLetterBitmap[j];
                int mask = (1 << (iFontCols-1));
                fY = fTopY - fPointSpace * j;
                for (int k = 0; mask > 0; k += 1, mask >>= 1)
                {
                    if (iRowBitmap & mask)
                        glVertex2f(fLeftX + k * fPointSpace, fY);
                }
            }
        }
        fLeftX += iFontCols * fPointSpace; 
    }

    // OpenGL cleanup
    glEnd();

    return true;
}

