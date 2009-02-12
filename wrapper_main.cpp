
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

// static global variables
static bool bFullscreen = false;
static bool bReturnWhenDone = false;
static bool bPrintFPS = false;

// static functions
static bool ParseArgs(int argc, void *argv[]);
static void PrintHelp(const char *pchProgName);
static bool InitSDL(void);

// external global functions from wrapper_opengl.cpp
extern bool InitGL(bool bPrintFPS);

// global functions used by other parts of the wrapper
bool CheckExitKey(void);

///////////////////////////////////////////////////////////////////////////////
// Main program function

int main(int argc, void *argv[])
{
    if (!ParseArgs(argc, argv))
        return 1;

    if (!InitSDL())
        return 2;

    if (!InitGL(bPrintFPS))
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

    // call the LOGO code
    tt_LogoMain();
    wrapper_glFlushVertices();
    SDL_GL_SwapBuffers();

    // wait until exit key pressed
    while (!bReturnWhenDone && !CheckExitKey())
        SDL_Delay(50);

    return 0;
}

///////////////////////////////////////////////////////////////////////////////
// global functions used in other parts of the wrapper

bool CheckExitKey(void)
{
    SDL_Event event;

    // Grab all the events off the queue.
    while (SDL_PollEvent(&event))
    {
        if (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE)
            return true;
        if (event.type == SDL_QUIT)
            return true;
    }

    return false;
}


///////////////////////////////////////////////////////////////////////////////
// Helper functions for the Main wrapper

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


