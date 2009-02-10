
/********************************************/
/* Turbo Turtle Logo Wrapper Functions      */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>

#include <SDL.h>
#include <SDL_opengl.h>
#include "wrapper_api.h"
#include "wrapper_pointtext.h"

// static global variables
static bool bRunning = true;
static bool bFullscreen = false;
static bool bReturnWhenDone = false;
static bool bPrintFPS = false;
static int iScreenWidth = 512;
static int iScreenHeight = 512;
static unsigned int uiClockFrameStart;

// real global variables
float fPixelsPerTurtleStep = 0.0;
int   iViewWidth = 0;
int   iViewHeight = 0;

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

    // set point and line smoothing
    glEnable(GL_POINT_SMOOTH);
    if (tt_LineSmooth > 0)
    {
        glEnable (GL_LINE_SMOOTH);
        if (tt_LineSmooth == 1)
            glHint (GL_LINE_SMOOTH_HINT, GL_FASTEST);
        else
            glHint (GL_LINE_SMOOTH_HINT, GL_NICEST);
    }

    // mark the start time
    uiClockFrameStart = SDL_GetTicks();

    // call the LOGO code
    tt_LogoMain();
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
        else if (strcmp((char *) argv[i], "--printfps") == 0)
            bPrintFPS = true;
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
    glColor3ub(255, 255, 255);

    return true;
}

///////////////////////////////////////////////////////////////////////////////
// Wrapper functions called from the Logo code

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

