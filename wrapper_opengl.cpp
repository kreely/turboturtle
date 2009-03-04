/********************************************/
/* Turbo Turtle Logo Wrapper Functions      */
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>
#include <math.h>

#include <SDL.h>
#include <SDL_opengl.h>
#include "wrapper_api.h"
#include "wrapper_pointtext.h"

#define MAX_VERTEX 1024

// globals used by other parts of the wrapper and/or the logo code
float fPixelsPerTurtleStep = 0.0;
int   iScreenWidth = 512;
int   iScreenHeight = 512;
int   iViewWidth = 0;
int   iViewHeight = 0;

// global functions defined in wrapper_main.cpp
extern bool CheckExitKey(void);

// static data used only by the opengl wrapper functions
static bool bPrintFPS = false;
static unsigned int uiClockFrameStart;
static float fLineVertex[MAX_VERTEX][2];
static unsigned char ucLineColors[MAX_VERTEX][4];
static float fPointVertex[MAX_VERTEX][2];
static unsigned char ucPointColors[MAX_VERTEX][4];
static int   iLineVertices;
static int   iPointVertices;

///////////////////////////////////////////////////////////////
// local (static) functions

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

///////////////////////////////////////////////////////////////
// wrapper functions called from other parts of the wrapper

bool InitGL(bool print_fps)
{
    bPrintFPS = print_fps;

    // Flat shading model
    glShadeModel(GL_FLAT);

    // Culling
    glDisable(GL_CULL_FACE);

    // Set the clear color
    glClearColor(0, 0, 0, 0);

    // Setup viewport
    glViewport(0, 0, iScreenWidth, iScreenHeight);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    // don't use perspective
    if (iScreenWidth <= iScreenHeight)
    {
        fPixelsPerTurtleStep = (float) iScreenWidth / (float) tt_WindowSize;
        iViewWidth = tt_WindowSize;
        iViewHeight = iScreenHeight * tt_WindowSize / iScreenWidth;
    }
    else
    {
        fPixelsPerTurtleStep = (float) iScreenHeight / (float) tt_WindowSize;
        iViewHeight = tt_WindowSize;
        iViewWidth = iScreenWidth * tt_WindowSize / iScreenHeight;
    }
    glOrtho(-iViewWidth/2, iViewWidth/2, -iViewHeight/2, iViewHeight/2, -1, 1);

    // set up z-buffer and alpha blending parameters
    glDisable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    // set up lighting
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glDisable(GL_LIGHTING);

    // clear the screen
    glClear(GL_COLOR_BUFFER_BIT);
    SDL_GL_SwapBuffers();
    glClear(GL_COLOR_BUFFER_BIT);
    glColor3ub(255, 255, 255);

    // mark the start time
    uiClockFrameStart = SDL_GetTicks();

    return true;
}

///////////////////////////////////////////////////////////////////////////////
// Wrapper functions called from the compiled Logo code

void wrapper_Clean(void)
{
    static float fFrameTimes[64], fTotalTime = 0.0;
    static int nFrames = 0, nFrameIdx = 0;

    // display the image being drawn
    wrapper_glFlushVertices();
    SDL_GL_SwapBuffers();

    // exit program if exit key was pressed
    if (CheckExitKey())
        exit(0);

    // paint the background and set up for drawing lines
    glClearColor(tt_ColorBackground[0]/255.0, tt_ColorBackground[1]/255.0, tt_ColorBackground[2]/255.0, 0);
    glClear(GL_COLOR_BUFFER_BIT);

    // delay until it's time to start the next frame
    unsigned int uiFrameDuration;
    if (tt_FramesPerSec == 0.0)
        uiFrameDuration = 0;
    else
        uiFrameDuration = (unsigned int) (1000.0 / tt_FramesPerSec);
    unsigned int uiThisFrameStart = uiClockFrameStart;
    unsigned int uiNextFrameStart = uiClockFrameStart + uiFrameDuration;
    unsigned int uiCurTime = SDL_GetTicks();
    if (uiCurTime >= (uiNextFrameStart - 2))
    {
        uiClockFrameStart = uiCurTime;
    }
    else
    {
        while ((uiCurTime = SDL_GetTicks()) < (uiNextFrameStart - 2))
        {
            if (CheckExitKey())
                exit(0);
            SDL_Delay(4);
        }
        uiClockFrameStart = uiNextFrameStart;
    }

    // print the frame rate if necessary
    if (bPrintFPS)
    {
        // calculate the average frame rate over last 64 frames
        if (nFrames == 64) fTotalTime -= fFrameTimes[nFrameIdx];
        fFrameTimes[nFrameIdx] = uiCurTime - uiThisFrameStart;
        fTotalTime += fFrameTimes[nFrameIdx];
        nFrameIdx = (nFrameIdx + 1) & 63;
        if (nFrames < 64) nFrames++;
        float fAverageTime = fTotalTime / (float) nFrames;
        // if there was more than 1 second in the last 64 frames, shrink the averaging window down to <= 1 sec
        if (fTotalTime > 1000.0)
        {
            float fSubSecTime = fTotalTime;
            int iOldIdx = (nFrameIdx - nFrames) & 63;
            int i1SecFrames = nFrames;
            while (fSubSecTime > 1000 && i1SecFrames > 1)
            {
                fSubSecTime -= fFrameTimes[iOldIdx];
                iOldIdx = (iOldIdx + 1) & 63;
                i1SecFrames--;
            }
            fAverageTime = fSubSecTime / (float) i1SecFrames;
        }
        float fFPS = 1000.0 / fAverageTime;
        // print it in a string
        char chMsg[16];
        sprintf(chMsg, "%.0f FPS", fFPS);
        // draw the string to the screen
        unsigned char textcolor[4] = {255, 255, 255, 0};
        glColor3ubv(textcolor);
        DrawPointText(0, 2, 2, tt_WindowSize/25, iViewWidth/2, -iViewHeight/2, chMsg);
    }

    return;
}

void wrapper_Erase(void)
{
    // flush any pending drawing operations
    wrapper_glFlushVertices();

    // paint the background and set up for drawing lines
    glClearColor(tt_ColorBackground[0]/255.0, tt_ColorBackground[1]/255.0, tt_ColorBackground[2]/255.0, 0);
    glClear(GL_COLOR_BUFFER_BIT);

    // exit program if exit key was pressed
    if (CheckExitKey())
        exit(0);
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
            else if (fInterceptY > 0.0 && fInterceptY < (float) iViewHeight)
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
            else if (fInterceptX > 0.0 && fInterceptX < (float) iViewWidth)
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
            else if (fInterceptY > 0.0 && fInterceptY < (float) iViewHeight)
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
            else if (fInterceptX > 0.0 && fInterceptX < (float) iViewWidth)
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
            else if (dInterceptY > 0.0 && dInterceptY < (double) iViewHeight)
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
            else if (dInterceptX > 0.0 && dInterceptX < (double) iViewWidth)
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
            else if (dInterceptY > 0.0 && dInterceptY < (double) iViewHeight)
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
            else if (dInterceptX > 0.0 && dInterceptX < (double) iViewWidth)
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

