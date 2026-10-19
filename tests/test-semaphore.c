#include <SDL.h>
#include <pthread.h>
#include <assert.h>
#include <stdio.h>
extern SDL_sem *__wrap_SDL_CreateSemaphore(Uint32);
extern void __wrap_SDL_DestroySemaphore(SDL_sem *);
extern int __wrap_SDL_SemWait(SDL_sem *);
extern int __wrap_SDL_SemTryWait(SDL_sem *);
extern int __wrap_SDL_SemWaitTimeout(SDL_sem *, Uint32);
extern int __wrap_SDL_SemPost(SDL_sem *);
extern Uint32 __wrap_SDL_SemValue(SDL_sem *);
static void *post(void *s) { assert(!__wrap_SDL_SemPost(s)); return NULL; }
int main(void) {
    SDL_sem *s = __wrap_SDL_CreateSemaphore(0);
    assert(s);
    assert(__wrap_SDL_SemTryWait(s) == SDL_MUTEX_TIMEDOUT);
    assert(__wrap_SDL_SemWaitTimeout(s, 5) == SDL_MUTEX_TIMEDOUT);
    for (unsigned i = 0; i < 100; ++i) {
        pthread_t t;
        assert(!pthread_create(&t, NULL, post, s));
        assert(!__wrap_SDL_SemWait(s));
        assert(!pthread_join(t, NULL));
        assert(!__wrap_SDL_SemValue(s));
    }
    assert(!__wrap_SDL_SemPost(s));
    assert(__wrap_SDL_SemValue(s) == 1);
    assert(!__wrap_SDL_SemTryWait(s));
    __wrap_SDL_DestroySemaphore(s);
    puts("PASS: semaphore startup handshakes, timeout and count");
}
