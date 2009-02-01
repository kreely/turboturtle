
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

// global variables
static bool bRunning = true;
static unsigned int uiClockFrameStart;

// static functions
static bool InitSDL(int *piScreenWidth, int *piScreenHeight, bool bFullscreen);
static bool InitGL(int iWidth, int iHeight);
static bool CheckExitKey(void);

///////////////////////////////////////////////////////////////////////////////
// Main program function

int main(int argc, void *argv[])
{
    int iWidth = 500;
    int iHeight = 500;

    if (!InitSDL(&iWidth, &iHeight, false))
        return 1;

    if (!InitGL(iWidth, iHeight))
        return 2;

    // mark the start time
    uiClockFrameStart = SDL_GetTicks();

    // call the LOGO code
    glBegin(GL_LINES);
    tt_LogoMain();
    glEnd();
    SDL_GL_SwapBuffers();

    // wait until exit key pressed
    while (!CheckExitKey())
        SDL_Delay(50);

    return 0;
}

///////////////////////////////////////////////////////////////////////////////
// Helper functions for the wrapper

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

bool InitSDL(int *piScreenWidth, int *piScreenHeight, bool bFullscreen)
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
        if (SDL_SetVideoMode(*piScreenWidth, *piScreenHeight, iBPP, iFlags) == 0)
            {
            printf("Video mode set failed: %s\n", SDL_GetError());
            return false;
            }
        // get current screen resolution
        SDL_Surface *pScreen = SDL_GetVideoSurface();
        *piScreenWidth = pScreen->w;
        *piScreenHeight = pScreen->h;
        }
    else
        {
        // create a windowed surface with the given dimensions
        if (SDL_SetVideoMode(*piScreenWidth, *piScreenHeight, iBPP, iFlags) == 0)
            {
            printf("Video mode set failed: %s\n", SDL_GetError());
            return false;
            }
        }

    // set window name
    SDL_WM_SetCaption("Turbo Turtle LOGO Animation", "TurboTurtle");

    return true;
}

bool InitGL(int iWidth, int iHeight)
{
    // Flat shading model
    glShadeModel(GL_FLAT);

    // Culling
    glDisable(GL_CULL_FACE);

    // Set the clear color
    glClearColor(0, 0, 0, 0);

    // Setup viewport
    glViewport(0, 0, iWidth, iHeight);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    // don't use perspective
    glOrtho(-tt_WindowSize/2, tt_WindowSize/2, -tt_WindowSize/2, tt_WindowSize/2, -1, 1);

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
    glClearColor(tt_ColorBackground[0], tt_ColorBackground[1], tt_ColorBackground[2], 0);
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

void wrapper_DrawLineSegment(float *pfOrigPos, float *pfNewPos, bool bWrapEnabled)
{
}

void wrapper_DrawLineSegment(double *pdOrigPos, double *pdNewPos, bool bWrapEnabled)
{
}

