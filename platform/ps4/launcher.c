#include "ps4gl-display.h"
#include "ps4gl-frame.h"
#include "ps4gl-sdl.h"
#include "ps4libc-threading.h"
#include "vk_ps4_log.h"
#include <SDL.h>
#include <orbis/SystemService.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>

static PS4GLDisplayOwner display;
static PS4GLFrameOwner frames;
static SDL_Window *window;
static SDL_GLContext context;
static SDL_GameController *pad;
static GLuint backdrop, font;
static unsigned char widths[96];
static FILE *logfile;
static int selected, help;
static char data[2][128];
static char message[160];
extern void descent_setup_controller(void);

static int begin(void *p) { return ps4glFrameBegin(p); }
static int present(void *p) { return ps4glFramePresent(p); }
static int quiesce(void *p) {
    if (frames.state && !frames.failed && ps4glFramePresent(p)) return -1;
    return ps4glFrameQuiesce(p);
}
static int exists(const char *root, const char *file) {
    char path[256]; snprintf(path, sizeof(path), "%s/%s", root, file);
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f); return 1;
}
static int complete(int game, const char *path) {
    if (game == 0) return exists(path,"descent.hog") && exists(path,"descent.pig");
    return (exists(path,"d2demo.hog") && exists(path,"d2demo.ham") && exists(path,"d2demo.pig")) ||
        (exists(path,"descent2.hog") && exists(path,"descent2.ham") && exists(path,"groupa.pig"));
}
static void scan_data(void) {
    for (int g = 0; g < 2; ++g) {
        snprintf(data[g], sizeof(data[g]), "/data/descent-ps4/d%d/data", g+1);
        if (complete(g, data[g])) continue;
        int usb;
        for (usb = 0; usb < 8; ++usb) {
            snprintf(data[g], sizeof(data[g]), "/mnt/usb%d/descent-ps4/d%d/data", usb, g+1);
            if (complete(g, data[g])) break;
        }
        if (usb == 8) data[g][0] = 0;
    }
}
static GLuint texture(FILE *f, int w, int h) {
    size_t bytes = (size_t)w*h*4;
    unsigned char *pixels = malloc(bytes);
    if (!pixels) return 0;
    if (fread(pixels, 1, bytes, f) != bytes) { free(pixels); return 0; }
    GLuint t; glGenTextures(1, &t); glBindTexture(GL_TEXTURE_2D, t);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
    free(pixels); return t;
}
static void quad(float x, float y, float w, float h, float r, float g, float b, float a) {
    glDisable(GL_TEXTURE_2D); glColor4f(r,g,b,a); glBegin(GL_QUADS);
    glVertex3f(x,y,0); glVertex3f(x+w,y,0); glVertex3f(x+w,y+h,0); glVertex3f(x,y+h,0); glEnd();
}
static void image_quad(GLuint t, float x, float y, float w, float h,
                       float u, float v, float uw, float vh) {
    glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D,t); glBegin(GL_QUADS);
    glTexCoord2f(u,v); glVertex3f(x,y,0);
    glTexCoord2f(u+uw,v); glVertex3f(x+w,y,0);
    glTexCoord2f(u+uw,v+vh); glVertex3f(x+w,y+h,0);
    glTexCoord2f(u,v+vh); glVertex3f(x,y+h,0); glEnd();
}
static void text(float x, float y, float scale, const char *s, float r, float g, float b) {
    glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D,font);
    glColor4f(r,g,b,1); glBegin(GL_QUADS);
    for (; *s; ++s) {
        unsigned c=(unsigned char)*s;
        if (c < 32 || c > 127) c='?';
        unsigned glyph=c-32;
        float u=(glyph%16)/16.f, v=(glyph/16)/6.f, w=32*scale, h=48*scale;
        glTexCoord2f(u,v); glVertex3f(x,y,0);
        glTexCoord2f(u+1/16.f,v); glVertex3f(x+w,y,0);
        glTexCoord2f(u+1/16.f,v+1/6.f); glVertex3f(x+w,y+h,0);
        glTexCoord2f(u,v+1/6.f); glVertex3f(x,y+h,0);
        x+=(widths[glyph]+1)*scale;
    }
    glEnd();
}
static void draw(void) {
    glViewport(0,0,1280,720);
    glClearColor(0.01f,0.015f,0.025f,1); glClear(GL_COLOR_BUFFER_BIT);
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(0,1280,720,0,-1,1);
    glMatrixMode(GL_MODELVIEW); glLoadIdentity();
    glDisable(GL_DEPTH_TEST); glDisable(GL_CULL_FACE); glDisable(GL_ALPHA_TEST);
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(1,1,1,1); image_quad(backdrop,0,0,1280,720,0,0,1,1);
    quad(0,0,1280,720,0.01f,0.02f,0.04f,0.25f);
    quad(72,78,44,3,1,.54f,.19f,1);
    text(130,57,.65f,"SIX DEGREES OF FREEDOM",.65f,.78f,.88f);
    text(68,96,2.5f,"DESCENT",.94f,.97f,1);
    text(75,208,.9f,"I + II  /  COLLECTION",.98f,.61f,.26f);
    text(75,270,.7f,"CHOOSE YOUR DESCENT",.7f,.78f,.84f);
    for (int g=0;g<2;++g) {
        float x=76+g*568, y=338;
        int active=selected==g;
        float pulse=active ? .68f+.2f*sinf(SDL_GetTicks()*.0025f) : .22f;
        quad(x-2,y-2,538,214,active ? 1:.35f,active ? .55f:.48f,active ? .22f:.6f,pulse);
        quad(x,y,534,210,.018f,.03f,.05f,.94f);
        quad(x,y,4,210,active ? 1:.25f,active ? .55f:.4f,active ? .22f:.55f,1);
        text(x+28,y+17,.65f,g ? "02  /  INTO THE ABYSS" : "01  /  INTO THE MINES",.61f,.72f,.81f);
        text(x+26,y+54,1.55f,g ? "DESCENT II" : "DESCENT I",active ? 1:.62f,active ? .94f:.7f,active ? .83f:.76f);
        text(x+28,y+126,.66f,g ? "Deeper mines. Deadlier machines." : "The original six-axis combat classic.",.65f,.73f,.8f);
        const char *status=!data[g][0] ? "GAME DATA NOT FOUND" : data[g][1]=='d' ? "READY  /  HDD" : "READY  /  USB";
        text(x+28,y+165,.60f,status,data[g][0] ? .48f:1,data[g][0] ? .82f:.42f,.66f);
    }
    if (message[0]) text(78,563,.63f,message,1,.65f,.3f);
    else text(78,563,.60f,pad ? "YOUR PILOTS AND SAVES STAY ON HDD" : "CONNECT A CONTROLLER TO CONTINUE",.65f,.74f,.82f);
    quad(76,625,1128,1,.4f,.55f,.65f,.5f);
    text(78,644,.64f,"LEFT / RIGHT  Select     X  Launch     TRIANGLE  Help     CIRCLE  Exit",.8f,.86f,.91f);
    if (help) {
        quad(0,0,1280,720,0,0,0,.68f);
        quad(180,130,920,460,.025f,.045f,.07f,.98f);
        quad(180,130,920,3,1,.55f,.22f,1);
        text(220,158,1.2f,"FLIGHT SYSTEMS",1,.8f,.53f);
        text(220,230,.75f,"LEFT STICK   Forward / reverse / strafe",.85f,.9f,1);
        text(220,277,.75f,"RIGHT STICK  Aim     L1 / R1  Roll",.85f,.9f,1);
        text(220,324,.75f,"R2  Primary fire     L2  Missiles",.85f,.9f,1);
        text(220,386,.65f,"Game data: /data/descent-ps4/d1/data or d2/data",.65f,.8f,.87f);
        text(220,425,.65f,"USB fallback: /mnt/usb0/descent-ps4/d1/data (or d2)",.65f,.8f,.87f);
        text(220,499,.7f,"X / TRIANGLE / CIRCLE  Back",1,.65f,.3f);
    }
    SDL_GL_SwapWindow(window);
}
static int graphics_init(void) {
    if (ps4glDisplayInit(&display)) return -1;
    if (ps4glFrameInit(&frames,display.device,display.queue,display.swap,display.pass,
        display.images,display.targets,display.width,display.height)) return -1;
    memcpy(frames.depth_images,display.depth_images,sizeof(frames.depth_images));
    PS4GLSDLOwner owner={.physical=display.physical,.device=display.device,.pass=display.pass,
        .width=display.width,.height=display.height,.depth_stencil=1,
        .begin=begin,.present=present,.quiesce=quiesce,.data=&frames};
    if (ps4glSDLSetOwner(&owner) || SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)) return -1;
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,2); SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE,0); SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE,0);
    window=SDL_CreateWindow("Descent I + II",0,0,1280,720,SDL_WINDOW_OPENGL);
    if (!window || !(context=SDL_GL_CreateContext(window))) return -1;
    FILE *f=fopen("/app0/launcher/hangar.rgba","rb");
    if (!f) return -1;
    backdrop=texture(f,1280,720); fclose(f);
    f=fopen("/app0/launcher/font.bin","rb");
    if (!f) return -1;
    int ok=fread(widths,1,sizeof(widths),f)==sizeof(widths);
    font=ok ? texture(f,512,288) : 0; fclose(f);
    for (int i=0;i<SDL_NumJoysticks();++i) if (SDL_IsGameController(i)) { pad=SDL_GameControllerOpen(i); if(pad) break; }
    return backdrop && font ? 0 : -1;
}
static void graphics_close(void) {
    if (pad) SDL_GameControllerClose(pad);
    pad=NULL;
    if (context) { glDeleteTextures(1,&backdrop); glDeleteTextures(1,&font); SDL_GL_DeleteContext(context); }
    context=NULL;
    if (window) SDL_DestroyWindow(window);
    window=NULL; SDL_Quit();
    if (!ps4glSDLSetOwner(NULL) && !ps4glFrameDestroy(&frames)) ps4glDisplayDestroy(&display);
}
int main(void) {
    mkdir("/data/descent-ps4",0777);
    logfile=fopen("/data/descent-ps4/launcher.log","w");
    if (!logfile) return 2;
    setvbuf(logfile,NULL,_IONBF,0);
    fputs("Descent Collection launcher 0.06\n",logfile);
    ps4EnableLibcLocks(); descent_setup_controller();
    vk_ps4_log_open("/data/descent-ps4/launcher-vulkan.log");
    FILE *choice=fopen("/data/descent-ps4/launcher.choice","rb");
    if (choice) { selected=fgetc(choice)=='2'; fclose(choice); }
    scan_data();
restart:
    if (graphics_init()) { fprintf(logfile,"FAIL graphics: %s\n",SDL_GetError()); return 3; }
    fprintf(logfile,"READY selection=%d controller=%d data1=%s data2=%s\n",selected+1,!!pad,data[0],data[1]);
    Uint32 next_axis=0, next_scan=SDL_GetTicks()+3000;
    int request=-1;
    while (request<0) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type==SDL_CONTROLLERDEVICEADDED && !pad && SDL_IsGameController(event.cdevice.which)) pad=SDL_GameControllerOpen(event.cdevice.which);
            if (event.type==SDL_CONTROLLERDEVICEREMOVED && pad && !SDL_GameControllerGetAttached(pad)) { SDL_GameControllerClose(pad); pad=NULL; }
            if (event.type==SDL_QUIT) request=0;
            if (event.type!=SDL_CONTROLLERBUTTONDOWN) continue;
            int b=event.cbutton.button;
            if (help) { if (b==SDL_CONTROLLER_BUTTON_A || b==SDL_CONTROLLER_BUTTON_B || b==SDL_CONTROLLER_BUTTON_Y) help=0; continue; }
            if (b==SDL_CONTROLLER_BUTTON_DPAD_LEFT || b==SDL_CONTROLLER_BUTTON_LEFTSHOULDER) { selected=0; message[0]=0; }
            if (b==SDL_CONTROLLER_BUTTON_DPAD_RIGHT || b==SDL_CONTROLLER_BUTTON_RIGHTSHOULDER) { selected=1; message[0]=0; }
            if (b==SDL_CONTROLLER_BUTTON_Y) help=1;
            if (b==SDL_CONTROLLER_BUTTON_B) request=0;
            if (b==SDL_CONTROLLER_BUTTON_A) {
                scan_data();
                if (data[selected][0]) request=selected+1;
                else snprintf(message,sizeof(message),"Missing data. Press TRIANGLE for HDD / USB paths.");
            }
        }
        if (!help && pad && SDL_GetTicks()>=next_axis) {
            int axis=SDL_GameControllerGetAxis(pad,SDL_CONTROLLER_AXIS_LEFTX);
            if (axis < -16000 || axis > 16000) { selected=axis>0; message[0]=0; next_axis=SDL_GetTicks()+200; }
        }
        if (SDL_GetTicks()>=next_scan) { scan_data(); next_scan=SDL_GetTicks()+3000; }
        if (request>0) snprintf(message,sizeof(message),"STARTING DESCENT %s...",request==1 ? "I":"II");
        draw();
        if (frames.failed) { fprintf(logfile,"FAIL rendering %d\n",frames.last_result); return 4; }
        SDL_Delay(8);
    }
    if (request) {
        choice=fopen("/data/descent-ps4/launcher.choice","wb");
        if (choice) { fputc(request==1?'1':'2',choice); fclose(choice); }
    }
    graphics_close();
    const char *target=request==1?"/app0/descent1.bin":request==2?"/app0/descent2.bin":"exit";
    fprintf(logfile,"LOAD %s\n",target);
    const char *args[]={target,NULL};
    int result=sceSystemServiceLoadExec(target,args);
    fprintf(logfile,"LoadExec returned %d\n",result);
    if (result<0) { snprintf(message,sizeof(message),"Launch failed (%d). Press X to retry.",result); goto restart; }
    for (;;) sleep(1);
}
