/* Convert Descent's U8 mixer output to the PS4 audio driver's S16/48 kHz. */
#include <SDL.h>
#include <string.h>
static SDL_AudioStream *converter;
static SDL_AudioSpec source;
extern int __real_SDL_OpenAudio(SDL_AudioSpec *, SDL_AudioSpec *);
extern void __real_SDL_CloseAudio(void);
static void mix(void *unused, Uint8 *output, int length) {
    (void)unused;
    memset(output, 0, length);
    Uint8 chunk[1024];
    unsigned attempts = 0;
    while (SDL_AudioStreamAvailable(converter) < length && attempts++ < 32) {
        memset(chunk, source.silence, sizeof(chunk));
        source.callback(source.userdata, chunk, sizeof(chunk));
        if (SDL_AudioStreamPut(converter, chunk, sizeof(chunk)) < 0) return;
    }
    SDL_AudioStreamGet(converter, output, length);
}
int __wrap_SDL_OpenAudio(SDL_AudioSpec *desired, SDL_AudioSpec *obtained) {
    if (!desired || !desired->callback || desired->format != AUDIO_U8 || desired->channels != 2)
        return SDL_SetError("Unsupported Descent mixer configuration");
    if (converter) return SDL_SetError("Descent audio already open");
    source = *desired;
    source.silence = 0x80;
    converter = SDL_NewAudioStream(source.format, source.channels, source.freq, AUDIO_S16SYS, 2, 48000);
    if (!converter) return -1;
    SDL_AudioSpec hardware = {0};
    hardware.freq = 48000; hardware.format = AUDIO_S16SYS; hardware.channels = 2;
    hardware.samples = 1024; hardware.callback = mix;
    int result = __real_SDL_OpenAudio(&hardware, NULL);
    if (result < 0) { SDL_FreeAudioStream(converter); converter = NULL; return result; }
    if (obtained) *obtained = source;
    return 0;
}
void __wrap_SDL_CloseAudio(void) {
    __real_SDL_CloseAudio();
    SDL_FreeAudioStream(converter);
    converter = NULL;
}
