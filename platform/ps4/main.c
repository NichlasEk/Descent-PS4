#include "ps4gl-display.h"
#include "ps4gl-frame.h"
#include "ps4gl-sdl.h"
#include "ps4libc-threading.h"
#include "vk_ps4_log.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef DESCENT_GAME
#define DESCENT_GAME 1
#endif
static PS4GLDisplayOwner display;
static PS4GLFrameOwner frames;
static FILE *logfile;
void descent_finish_frame(void) {
    // Descent calls this around swap; submit a live frame before waiting.
    if (frames.state && !frames.failed) ps4glFramePresent(&frames);
    if (display.device) vkDeviceWaitIdle(display.device);
}
static int begin(void *p) { return ps4glFrameBegin(p); }
static int present(void *p) {
    GLenum error = glGetError();
    if (error && frames.frames < 8) fprintf(logfile, "GL error before swap: %x\n", error);
    int result = ps4glFramePresent(p);
    if (frames.frames < 4 || result)
        fprintf(logfile, "frame %u result %d\n", frames.frames, result);
    return result;
}
static int quiesce(void *p) {
    if (frames.state && !frames.failed && ps4glFramePresent(p)) return -1;
    return ps4glFrameQuiesce(p);
}
static int exists(const char *root, const char *name) {
    char path[512];
    snprintf(path, sizeof(path), "%s/%s", root, name);
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}
static int complete(const char *root) {
#if DESCENT_GAME == 1
    return exists(root, "descent.hog") && exists(root, "descent.pig");
#else
    return (exists(root, "d2demo.hog") && exists(root, "d2demo.ham") && exists(root, "d2demo.pig")) ||
           (exists(root, "descent2.hog") && exists(root, "descent2.ham") && exists(root, "groupa.pig"));
#endif
}
extern int __real_main(int, char **);
extern void descent_setup_controller(void);
int __wrap_main(int argc, char **argv) {
    (void)argc; (void)argv;
    mkdir("/data/descent-ps4", 0777);
    char profile[128], logpath[160], data[128];
    snprintf(profile, sizeof(profile), "/data/descent-ps4/d%d", DESCENT_GAME);
    mkdir(profile, 0777);
    snprintf(logpath, sizeof(logpath), "%s/boot.log", profile);
    logfile = fopen(logpath, "w");
    if (!logfile) return 2;
    setvbuf(logfile, NULL, _IONBF, 0);
    fprintf(logfile, "Descent %d engine startup\n", DESCENT_GAME);
    ps4EnableLibcLocks();
    descent_setup_controller();
    snprintf(data, sizeof(data), "%s/data", profile);
    if (!complete(data)) {
        int i;
        for (i = 0; i < 8; ++i) {
            snprintf(data, sizeof(data), "/mnt/usb%d/descent-ps4/d%d/data", i, DESCENT_GAME);
            if (complete(data)) break;
        }
        if (i == 8) { fputs("STOP: no complete HDD/USB game data\n", logfile); return 3; }
    }
    fprintf(logfile, "data: %s\n", data);
    setenv(DESCENT_GAME == 1 ? "D1X_REBIRTH_HOME" : "D2X_REBIRTH_HOME", profile, 1);
    snprintf(logpath, sizeof(logpath), "%s/vulkan.log", profile);
    vk_ps4_log_open(logpath);
    if (ps4glDisplayInit(&display)) { fputs("FAIL display\n", logfile); return 4; }
    if (ps4glFrameInit(&frames, display.device, display.queue, display.swap,
        display.pass, display.images, display.targets, display.width, display.height)) return 5;
    memcpy(frames.depth_images, display.depth_images, sizeof(frames.depth_images));
    PS4GLSDLOwner owner = {.physical=display.physical, .device=display.device,
        .pass=display.pass, .width=display.width, .height=display.height,
        .depth_stencil=1, .begin=begin, .present=present, .quiesce=quiesce, .data=&frames};
    if (ps4glSDLSetOwner(&owner)) return 6;
    fputs("PASS display; entering game main\n", logfile);
    char *args[] = {"/app0/eboot.bin", "-hogdir", data, "-window", "-notitles", "-nomovies", "-nomusic",
        "-gl_syncmethod", "0", "-gl_intensity4_ok", "0", "-gl_luminance4_alpha4_ok", "0", "-gl_rgba2_ok", "0", NULL};
    int result = __real_main((int)(sizeof(args) / sizeof(args[0]) - 1), args);
    fprintf(logfile, "game returned %d\n", result);
    if (!ps4glSDLSetOwner(NULL) && !ps4glFrameDestroy(&frames)) ps4glDisplayDestroy(&display);
    fclose(logfile);
    return result;
}
