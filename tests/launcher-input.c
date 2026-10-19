/* Xvfb-only helper, used by smoke-launcher.sh. */
#include <X11/Xlib.h>
#include <X11/extensions/XTest.h>
#include <unistd.h>
int main(int argc, char **argv) {
    Display *d=XOpenDisplay(NULL);
    if (!d) return 1;
    Window root=DefaultRootWindow(d), parent, returned, *children;
    unsigned count; int found=0;
    if (XQueryTree(d,root,&returned,&parent,&children,&count)) {
        for(unsigned i=0;i<count;++i) {
            XWindowAttributes a;
            if (XGetWindowAttributes(d,children[i],&a) && a.map_state==IsViewable && a.width>=640) {
                XSetInputFocus(d,children[i],RevertToParent,CurrentTime); found=1; break;
            }
        }
        XFree(children);
    }
    if (!found) { XCloseDisplay(d); return 2; }
    for(int i=1;i<argc;++i) {
        KeyCode key=XKeysymToKeycode(d,XStringToKeysym(argv[i]));
        if(!key) return 3;
        XTestFakeKeyEvent(d,key,True,CurrentTime); XFlush(d); usleep(120000);
        XTestFakeKeyEvent(d,key,False,CurrentTime); XFlush(d); usleep(350000);
    }
    XCloseDisplay(d); return 0;
}
