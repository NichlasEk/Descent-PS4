#include <SDL.h>
#include <assert.h>
#include <stdio.h>
extern int __wrap_SDL_PrivateJoystickAxis(SDL_Joystick *, Uint8, Sint16);
extern void descent_setup_controller(void);
static Uint8 observed_axis;
static Sint16 observed_value;
int __real_SDL_PrivateJoystickAxis(SDL_Joystick *pad, Uint8 axis, Sint16 value) {
    (void)pad; observed_axis = axis; observed_value = value; return 7;
}
int main(void) {
    const Uint8 raw[] = {0,1,2,4,5,6}, normalized[] = {0,1,2,3,4,5};
    for (unsigned i = 0; i < 6; ++i)
        for (int value = -32768; value <= 32767; ++value) {
            assert(__wrap_SDL_PrivateJoystickAxis(NULL, raw[i], value) == 7);
            assert(observed_axis == normalized[i] && observed_value == value);
        }
    descent_setup_controller();
    assert(SDL_Init(SDL_INIT_GAMECONTROLLER) == 0);
    SDL_JoystickGUID guid = SDL_JoystickGetGUIDFromString("01800000000000000000000000000000");
    char *mapping = SDL_GameControllerMappingForGUID(guid);
    assert(mapping);
    SDL_free(mapping); SDL_Quit();
    puts("PASS 393216 axis values and GameController mapping registration");
}
