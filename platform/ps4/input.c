#include <SDL.h>
/* The linked PS4 backend emits 0,1,2,4,5,6 despite declaring six axes.
 * Normalize its three upper slots before SDL validates the axis index. */
extern int __real_SDL_PrivateJoystickAxis(SDL_Joystick *, Uint8, Sint16);
int __wrap_SDL_PrivateJoystickAxis(SDL_Joystick *pad, Uint8 axis, Sint16 value) {
    if (axis >= 4 && axis <= 6) --axis;
    return __real_SDL_PrivateJoystickAxis(pad, axis, value);
}
void descent_setup_controller(void) {
    SDL_SetHint(SDL_HINT_GAMECONTROLLERCONFIG,
        "01800000000000000000000000000000,PS4 DualShock 4,"
        "a:b0,b:b1,x:b2,y:b3,leftshoulder:b4,rightshoulder:b5,"
        "back:b17,start:b9,leftstick:b11,rightstick:b12,"
        "dpup:b13,dpdown:b14,dpleft:b15,dpright:b16,"
        "leftx:a0,lefty:a1,lefttrigger:a2,rightx:a3,righty:a4,righttrigger:a5,");
}
