
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

// static global variables
static bool bRunning = true;
static bool bFullscreen = false;
static bool bReturnWhenDone = false;
static int iScreenWidth = 512;
static int iScreenHeight = 512;
static int iViewWidth = 0;
static int iViewHeight = 0;
static unsigned int uiClockFrameStart;

// real global variables
float fPixelsPerTurtleStep = 0.0;

// static functions
static bool ParseArgs(int argc, void *argv[]);
static void PrintHelp(const char *pchProgName);
static bool InitSDL(void);
static bool InitGL(void);
static bool CheckExitKey(void);

///////////////////////////////////////////////////////////////////////////////
// Main program function

int main(int argc, void *argv[])
{
    if (!ParseArgs(argc, argv))
        return 1;

    if (!InitSDL())
        return 2;

    if (!InitGL())
        return 3;

    // set line smoothing
    if (tt_LineSmooth > 0)
    {
        glEnable (GL_LINE_SMOOTH);
        glEnable (GL_BLEND);
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        if (tt_LineSmooth == 1)
            glHint (GL_LINE_SMOOTH_HINT, GL_FASTEST);
        else
            glHint (GL_LINE_SMOOTH_HINT, GL_NICEST);
    }

    // mark the start time
    uiClockFrameStart = SDL_GetTicks();

    // call the LOGO code
    glBegin(GL_LINES);
    tt_LogoMain();
    glEnd();
    SDL_GL_SwapBuffers();

    // wait until exit key pressed
    while (!bReturnWhenDone && !CheckExitKey())
        SDL_Delay(50);

    return 0;
}

///////////////////////////////////////////////////////////////////////////////
// Helper functions for the wrapper

bool ParseArgs(int argc, void *argv[])
{
    bool bCustomRes = false;

    for (int i = 1; i < argc; i++)
    {
        if (strcmp((char *) argv[i], "--fullscreen") == 0)
        {
            bFullscreen = true;
            if (!bCustomRes)
            {
                iScreenWidth = 1024;        //default to 1024x768 if --fullscreen is given
                iScreenHeight = 768;
            }
        }
        else if (strcmp((char *) argv[i], "--exitwhendone") == 0)
            bReturnWhenDone = true;
        else if (strcmp((char *) argv[i], "--help") == 0)
        {
            PrintHelp((char *) argv[0]);
            return false;
        }
        else if (strcmp((char *) argv[i], "--resolution") == 0)
        {
            bCustomRes = true;
            if (argc - i - 1 < 2)
            {
                PrintHelp((char *) argv[0]);
                printf("Error: --resolution option given but missing XSIZE and/or YSIZE.\n\n");
                return false;
            }
            iScreenWidth = atoi((char *) argv[i+1]);
            iScreenHeight = atoi((char *) argv[i+2]);
            i += 2;
        }
        else
        {
            PrintHelp((char *) argv[0]);
            printf("Error: Invalid option '%s'\n\n", argv[i]);
            return false;
        }
    }
    return true;
}

void PrintHelp(const char *pchProgName)
{
    printf("%s - A TurboTurtle Logo Program\n\n", pchProgName);
    printf("Options:\n");
    printf("  --help                    - Print this message\n");
    printf("  --resolution XSIZE YSIZE  - Set the window or fullscreen resolution to XSIZE x YSIZE\n");
    printf("  --fullscreen              - Set fullscreen video mode\n");
    printf("  --exitwhendone            - Exit immediately when done instead of waiting for Escape\n");
    printf("\n");
}

bool CheckExitKey(void)
{
    SDL_Event event;

    // Grab all the events off the queue.
    while (SDL_PollEvent(&event))
    {
        if (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE)
            return true;
    }

    return false;
}

bool InitSDL(void)
{
    const SDL_VideoInfo* psInfo = NULL;
    int iBPP = 0;
    int iFlags = 0;

    // First, initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0)
        {
        printf("Video initialization failed: %s\n", SDL_GetError());
        return false;
        }
    atexit(SDL_Quit);

    // Get display information.
    psInfo = SDL_GetVideoInfo( );
    iBPP = psInfo->vfmt->BitsPerPixel;

    SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 5);      // at least 5 bits of red
    SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 5);    // at least 5 bits of green
    SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 5);     // at least 5 bits of blue
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);  // use double-buffered screen

    iFlags = SDL_OPENGL;
    if (bFullscreen)
        {
        iFlags |= SDL_FULLSCREEN;
        if (SDL_SetVideoMode(iScreenWidth, iScreenHeight, iBPP, iFlags) == 0)
            {
            printf("Video mode set failed: %s\n", SDL_GetError());
            return false;
            }
        // get current screen resolution
        SDL_Surface *pScreen = SDL_GetVideoSurface();
        iScreenWidth = pScreen->w;
        iScreenHeight = pScreen->h;
        SDL_ShowCursor(SDL_DISABLE);
        }
    else
        {
        // create a windowed surface with the given dimensions
        if (SDL_SetVideoMode(iScreenWidth, iScreenHeight, iBPP, iFlags) == 0)
            {
            printf("Video mode set failed: %s\n", SDL_GetError());
            return false;
            }
        }

    // set window name
    SDL_WM_SetCaption("Turbo Turtle LOGO Animation", "TurboTurtle");

    return true;
}

bool InitGL(void)
{
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

    // set up z-buffer parameters
    glDisable(GL_DEPTH_TEST);

    // set up lighting
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glDisable(GL_LIGHTING);

    // clear the screen
    glClear(GL_COLOR_BUFFER_BIT);
    SDL_GL_SwapBuffers();
    glColor3ub(255, 255, 255);

    return true;
}

///////////////////////////////////////////////////////////////////////////////
// Wrapper functions called from the Logo code

void wrapper_Clean(void)
{
    // display the image being drawn
    glEnd();
    SDL_GL_SwapBuffers();

    // exit program if exit key was pressed
    if (CheckExitKey())
        exit(0);

    // paint the background and set up for drawing lines
    glClearColor(tt_ColorBackground[0]/255.0, tt_ColorBackground[1]/255.0, tt_ColorBackground[2]/255.0, 0);
    glClear(GL_COLOR_BUFFER_BIT);
    glBegin(GL_LINES);

    // if framespersec == 0, return right away
    if (tt_FramesPerSec == 0.0)
        return;

    // otherwise, delay until it's time to start the next frame
    unsigned int uiFrameDuration = (unsigned int) (1000.0 / tt_FramesPerSec);
    unsigned int uiNextFrameStart = uiClockFrameStart + uiFrameDuration;
    unsigned int uiCurTime = SDL_GetTicks();
    if (uiCurTime >= (uiNextFrameStart - 2))
    {
        uiClockFrameStart = uiCurTime;
        return;
    }
    while (SDL_GetTicks() < (uiNextFrameStart - 2))
    {
        if (CheckExitKey())
            exit(0);
        SDL_Delay(4);
    }
    uiClockFrameStart = uiNextFrameStart;
    return;
}

void wrapper_Erase(void)
{
    // paint the background and set up for drawing lines
    glEnd();
    glClearColor(tt_ColorBackground[0]/255.0, tt_ColorBackground[1]/255.0, tt_ColorBackground[2]/255.0, 0);
    glClear(GL_COLOR_BUFFER_BIT);
    glBegin(GL_LINES);

    // exit program if exit key was pressed
    if (CheckExitKey())
        exit(0);
}

void wrapper_DrawLineSegment(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled)
{
    if (!bWrapEnabled)
    {
        glVertex2f(pfOrigPos[0], pfOrigPos[1]);
        glVertex2f(pfNewPos[0], pfNewPos[1]);
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
            glVertex2f(fStartX - fWidthLimit, fStartY - fHeightLimit);
            glVertex2f(fEndX - fWidthLimit,   fEndY - fHeightLimit);
            return;
        }
        // otherwise, draw a line segment
        glVertex2f(fStartX - fWidthLimit, fStartY - fHeightLimit);
        glVertex2f(fEdgeX - fWidthLimit,  fEdgeY - fHeightLimit);
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

void wrapper_DrawLineSegment(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled)
{
    if (!bWrapEnabled)
    {
        glVertex2d(pdOrigPos[0], pdOrigPos[1]);
        glVertex2d(pdNewPos[0], pdNewPos[1]);
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
            glVertex2d(dStartX - dWidthLimit, dStartY - dHeightLimit);
            glVertex2d(dEndX - dWidthLimit,   dEndY - dHeightLimit);
            return;
        }
        // otherwise, draw a line segment
        glVertex2d(dStartX - dWidthLimit, dStartY - dHeightLimit);
        glVertex2d(dEdgeX - dWidthLimit,  dEdgeY - dHeightLimit);
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

