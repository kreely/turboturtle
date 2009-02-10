
/********************************************/
/* Turbo Turtle Logo Wrapper Functions      */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>
#include <math.h>

#include <SDL.h>
#include <SDL_opengl.h>
#include "wrapper_api.h"

#define MAX_VERTEX 1024

// these data are defined in wrapper_main.cpp
extern int iViewWidth;
extern int iViewHeight;

// global functions defined in wrapper_main.cpp
extern bool CheckExitKey(void);

// static data used only by the opengl wrapper functions
static float fLineVertex[MAX_VERTEX][2];
static unsigned char ucLineColors[MAX_VERTEX][4];
static float fPointVertex[MAX_VERTEX][2];
static unsigned char ucPointColors[MAX_VERTEX][4];
static int   iLineVertices;
static int   iPointVertices;

static void FlushLineVertices(void)
{
    if (CheckExitKey()) exit(0);

    if (iLineVertices > 0)
    {
	    glEnableClientState(GL_VERTEX_ARRAY);
	    glEnableClientState(GL_COLOR_ARRAY);
	
	    glVertexPointer(2, GL_FLOAT, 0, fLineVertex);
	    glColorPointer(3, GL_UNSIGNED_BYTE, 4, ucLineColors);
	    glDrawArrays(GL_LINES, 0, iLineVertices);
	
	    glDisableClientState(GL_VERTEX_ARRAY);
	    glDisableClientState(GL_COLOR_ARRAY);

        iLineVertices = 0;
    }
}

static void FlushPointVertices(void)
{
    if (CheckExitKey()) exit(0);

    if (iPointVertices > 0)
    {
	    glEnableClientState(GL_VERTEX_ARRAY);
	    glEnableClientState(GL_COLOR_ARRAY);
	
	    glVertexPointer(2, GL_FLOAT, 0, fPointVertex);
	    glColorPointer(3, GL_UNSIGNED_BYTE, 4, ucPointColors);
	    glDrawArrays(GL_POINTS, 0, iPointVertices);
	
	    glDisableClientState(GL_VERTEX_ARRAY);
	    glDisableClientState(GL_COLOR_ARRAY);

        iPointVertices = 0;
    }
}

void wrapper_glFlushVertices(void)
{
    FlushLineVertices();
    FlushPointVertices();
}

void wrapper_glLineVertex(float fVertexX, float fVertexY)
{
    fLineVertex[iLineVertices][0] = fVertexX;
    fLineVertex[iLineVertices][1] = fVertexY;
    *((int *) ucLineColors[iLineVertices]) = *((int *) tt_ActiveColor);
    iLineVertices++;
    if (iLineVertices == MAX_VERTEX)
        FlushLineVertices();
}

void wrapper_glPointVertex(float fVertexX, float fVertexY)
{
    fPointVertex[iPointVertices][0] = fVertexX;
    fPointVertex[iPointVertices][1] = fVertexY;
    *((int *) ucPointColors[iPointVertices]) = *((int *) tt_ActiveColor);
    iPointVertices++;
    if (iPointVertices == MAX_VERTEX)
        FlushPointVertices();
}

void wrapper_glDrawLineWrap(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled)
{
    if (!bWrapEnabled)
    {
        wrapper_glLineVertex(pfOrigPos[0], pfOrigPos[1]);
        wrapper_glLineVertex(pfNewPos[0], pfNewPos[1]);
        return;
    }

    float fWidthLimit = (float) iViewWidth / 2.0;
    float fHeightLimit = (float) iViewHeight / 2.0;

    float fStartX = fmodf(pfOrigPos[0] + fWidthLimit, (float) iViewWidth);
    if (fStartX < 0.0) fStartX += (float) iViewWidth;
    float fStartY = fmodf(pfOrigPos[1] + fHeightLimit, (float) iViewHeight);
    if (fStartY < 0.0) fStartY += (float) iViewHeight;

    float fDeltaX = pfNewPos[0] - pfOrigPos[0];
    float fDeltaY = pfNewPos[1] - pfOrigPos[1];

    float fEndX = fStartX + fDeltaX;
    float fEndY = fStartY + fDeltaY;

    while(true)
    {
        float fEdgeX, fEdgeY;
        bool bWrapX = false, bWrapY = false;

        if (fEndX < 0.0)
        {
            float fInterceptY = fStartY - (fStartX - 0.0) * fDeltaY / fDeltaX;
            if (fInterceptY == 0.0)
            {
                fEdgeX = 0.0;
                fEdgeY = 0.0;
                bWrapX = bWrapY = true;
            }
            else if (fInterceptY > 0.0 and fInterceptY < (float) iViewHeight)
            {
                fEdgeX = 0.0;
                fEdgeY = fInterceptY;
                bWrapX = true;
            }
        }
        if (fEndY > (float) iViewHeight)
        {
            float fInterceptX = fStartX + ((float) iViewHeight - fStartY) * fDeltaX / fDeltaY;
            if (fInterceptX == 0.0)
            {
                fEdgeX = 0.0;
                fEdgeY = (float) iViewHeight;
                bWrapX = bWrapY = true;
            }
            else if (fInterceptX > 0.0 and fInterceptX < (float) iViewWidth)
            {
                fEdgeX = fInterceptX;
                fEdgeY = (float) iViewHeight;
                bWrapY = true;
            }
        }
        if (fEndX > (float) iViewWidth)
        {
            float fInterceptY = fStartY + ((float) iViewWidth - fStartX) * fDeltaY / fDeltaX;
            if (fInterceptY == (float) iViewHeight)
            {
                fEdgeX = (float) iViewWidth;
                fEdgeY = (float) iViewHeight;
                bWrapX = bWrapY = true;
            }
            else if (fInterceptY > 0.0 and fInterceptY < (float) iViewHeight)
            {
                fEdgeX = (float) iViewWidth;
                fEdgeY = fInterceptY;
                bWrapX = true;
            }
        }
        if (fEndY < 0.0)
        {
            float fInterceptX = fStartX - (fStartY - 0.0) * fDeltaX / fDeltaY;
            if (fInterceptX == (float) iViewWidth)
            {
                fEdgeX = (float) iViewWidth;
                fEdgeY = 0.0;
                bWrapX = bWrapY = true;
            }
            else if (fInterceptX > 0.0 and fInterceptX < (float) iViewWidth)
            {
                fEdgeX = fInterceptX;
                fEdgeY = 0.0;
                bWrapY = true;
            }
        }
        // if there was no wrap, just draw the line and return
        if (!bWrapX && !bWrapY)
        {
            wrapper_glLineVertex(fStartX - fWidthLimit, fStartY - fHeightLimit);
            wrapper_glLineVertex(fEndX - fWidthLimit,   fEndY - fHeightLimit);
            return;
        }
        // otherwise, draw a line segment
        wrapper_glLineVertex(fStartX - fWidthLimit, fStartY - fHeightLimit);
        wrapper_glLineVertex(fEdgeX - fWidthLimit,  fEdgeY - fHeightLimit);
        // adjust the start and end points
        if (bWrapX)
        {
            if (fEdgeX == 0.0)
                fEndX += (float) iViewWidth;
            else
                fEndX -= (float) iViewWidth;
            fStartX = (float) iViewWidth - fEdgeX;
        }
        else fStartX = fEdgeX;
        if (bWrapY)
        {
            if (fEdgeY == 0.0)
                fEndY += (float) iViewHeight;
            else
                fEndY -= (float) iViewHeight;
            fStartY = (float) iViewHeight - fEdgeY;
        }
        else fStartY = fEdgeY;
        // and loop again
    } // while(true)
}

void wrapper_glDrawLineWrap(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled)
{
    if (!bWrapEnabled)
    {
        wrapper_glLineVertex((float) pdOrigPos[0], (float) pdOrigPos[1]);
        wrapper_glLineVertex((float) pdNewPos[0],  (float) pdNewPos[1]);
        return;
    }

    double dWidthLimit = (double) iViewWidth / 2.0;
    double dHeightLimit = (double) iViewHeight / 2.0;

    double dStartX = fmod(pdOrigPos[0] + dWidthLimit, (double) iViewWidth);
    if (dStartX < 0.0) dStartX += (double) iViewWidth;
    double dStartY = fmod(pdOrigPos[1] + dHeightLimit, (double) iViewHeight);
    if (dStartY < 0.0) dStartY += (double) iViewHeight;

    double dDeltaX = pdNewPos[0] - pdOrigPos[0];
    double dDeltaY = pdNewPos[1] - pdOrigPos[1];

    double dEndX = dStartX + dDeltaX;
    double dEndY = dStartY + dDeltaY;

    while(true)
    {
        double dEdgeX, dEdgeY;
        bool bWrapX = false, bWrapY = false;

        if (dEndX < 0.0)
        {
            double dInterceptY = dStartY - (dStartX - 0.0) * dDeltaY / dDeltaX;
            if (dInterceptY == 0.0)
            {
                dEdgeX = 0.0;
                dEdgeY = 0.0;
                bWrapX = bWrapY = true;
            }
            else if (dInterceptY > 0.0 and dInterceptY < (double) iViewHeight)
            {
                dEdgeX = 0.0;
                dEdgeY = dInterceptY;
                bWrapX = true;
            }
        }
        if (dEndY > (double) iViewHeight)
        {
            double dInterceptX = dStartX + ((double) iViewHeight - dStartY) * dDeltaX / dDeltaY;
            if (dInterceptX == 0.0)
            {
                dEdgeX = 0.0;
                dEdgeY = (double) iViewHeight;
                bWrapX = bWrapY = true;
            }
            else if (dInterceptX > 0.0 and dInterceptX < (double) iViewWidth)
            {
                dEdgeX = dInterceptX;
                dEdgeY = (double) iViewHeight;
                bWrapY = true;
            }
        }
        if (dEndX > (double) iViewWidth)
        {
            double dInterceptY = dStartY + ((double) iViewWidth - dStartX) * dDeltaY / dDeltaX;
            if (dInterceptY == (double) iViewHeight)
            {
                dEdgeX = (double) iViewWidth;
                dEdgeY = (double) iViewHeight;
                bWrapX = bWrapY = true;
            }
            else if (dInterceptY > 0.0 and dInterceptY < (double) iViewHeight)
            {
                dEdgeX = (double) iViewWidth;
                dEdgeY = dInterceptY;
                bWrapX = true;
            }
        }
        if (dEndY < 0.0)
        {
            double dInterceptX = dStartX - (dStartY - 0.0) * dDeltaX / dDeltaY;
            if (dInterceptX == (double) iViewWidth)
            {
                dEdgeX = (double) iViewWidth;
                dEdgeY = 0.0;
                bWrapX = bWrapY = true;
            }
            else if (dInterceptX > 0.0 and dInterceptX < (double) iViewWidth)
            {
                dEdgeX = dInterceptX;
                dEdgeY = 0.0;
                bWrapY = true;
            }
        }
        // if there was no wrap, just draw the line and return
        if (!bWrapX && !bWrapY)
        {
            wrapper_glLineVertex((float) (dStartX - dWidthLimit), (float) (dStartY - dHeightLimit));
            wrapper_glLineVertex((float) (dEndX - dWidthLimit),   (float) (dEndY - dHeightLimit));
            return;
        }
        // otherwise, draw a line segment
        wrapper_glLineVertex((float) (dStartX - dWidthLimit), (float) (dStartY - dHeightLimit));
        wrapper_glLineVertex((float) (dEdgeX - dWidthLimit),  (float) (dEdgeY - dHeightLimit));
        // adjust the start and end points
        if (bWrapX)
        {
            if (dEdgeX == 0.0)
                dEndX += (double) iViewWidth;
            else
                dEndX -= (double) iViewWidth;
            dStartX = (double) iViewWidth - dEdgeX;
        }
        else dStartX = dEdgeX;
        if (bWrapY)
        {
            if (dEdgeY == 0.0)
                dEndY += (double) iViewHeight;
            else
                dEndY -= (double) iViewHeight;
            dStartY = (double) iViewHeight - dEdgeY;
        }
        else dStartY = dEdgeY;
        // and loop again
    } // while(true)
}

