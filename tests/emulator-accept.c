/* Test-only input, run on the isolated Xvfb display, never the desktop. */
#include <X11/Xlib.h>
#include <X11/extensions/XTest.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    Display *d = XOpenDisplay(NULL);
    if (!d) return 1;
    Window root = DefaultRootWindow(d), parent, returned, *children;
    unsigned count;
    int found = 0;
    if (XQueryTree(d, root, &returned, &parent, &children, &count)) {
        for (unsigned i = 0; i < count; ++i) {
            XWindowAttributes a;
            if (XGetWindowAttributes(d, children[i], &a) && a.map_state == IsViewable && a.width >= 640) {
                XSetInputFocus(d, children[i], RevertToParent, CurrentTime);
                found = 1; break;
            }
        }
        XFree(children);
    }
    if (!found) { XCloseDisplay(d); return 2; }
    KeyCode key = XKeysymToKeycode(d, XStringToKeysym("n"));
    for (unsigned i = 0; i < 8; ++i) {
        if (i == 7) key = XKeysymToKeycode(d, XStringToKeysym("b"));
        XTestFakeKeyEvent(d, key, True, CurrentTime); XFlush(d);
        usleep(150000);
        XTestFakeKeyEvent(d, key, False, CurrentTime); XFlush(d);
        sleep(2);
    }
    if (getenv("DESCENT_SMOKE_MOVE")) {
        const char *keys[] = {"w", "l", "o"};
        for (unsigned i = 0; i < 3; ++i) {
            key = XKeysymToKeycode(d, XStringToKeysym(keys[i]));
            XTestFakeKeyEvent(d, key, True, CurrentTime); XFlush(d);
            sleep(1);
            XTestFakeKeyEvent(d, key, False, CurrentTime); XFlush(d);
            usleep(250000);
        }
        puts("Applied left stick forward, right stick yaw and R2; inspect scene.");
    }
    XCloseDisplay(d);
    puts("Sent seven Cross presses and Circle to isolated emulator; inspect outcome.");
}
