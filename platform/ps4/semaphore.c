/* SDL semaphore adapter: avoid FreeBSD ksem imports absent in shadPS4.
 * Uses the same pthread primitives validated by the PS4 runtime probe.
 * As with SDL, callers must join users before destroying a semaphore. */
#include <SDL.h>
#include <pthread.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <stdint.h>
struct SDL_semaphore { pthread_mutex_t mutex; pthread_cond_t cond; Uint32 count; };
SDL_sem *__wrap_SDL_CreateSemaphore(Uint32 value) {
    SDL_sem *s = calloc(1, sizeof(*s));
    if (!s) return NULL;
    if (pthread_mutex_init(&s->mutex, NULL)) { free(s); return NULL; }
    if (pthread_cond_init(&s->cond, NULL)) {
        pthread_mutex_destroy(&s->mutex); free(s); return NULL;
    }
    s->count = value;
    return s;
}
void __wrap_SDL_DestroySemaphore(SDL_sem *s) {
    if (!s) return;
    pthread_cond_destroy(&s->cond); pthread_mutex_destroy(&s->mutex); free(s);
}
int __wrap_SDL_SemWaitTimeout(SDL_sem *s, Uint32 ms) {
    if (!s) return SDL_SetError("NULL semaphore");
    struct timespec end;
    if (ms && ms != SDL_MUTEX_MAXWAIT) {
        clock_gettime(CLOCK_REALTIME, &end);
        end.tv_sec += ms / 1000;
        end.tv_nsec += (ms % 1000) * 1000000L;
        if (end.tv_nsec >= 1000000000L) { ++end.tv_sec; end.tv_nsec -= 1000000000L; }
    }
    int rc = 0;
    pthread_mutex_lock(&s->mutex);
    while (!s->count) {
        if (!ms) { rc = ETIMEDOUT; break; }
        rc = ms == SDL_MUTEX_MAXWAIT ? pthread_cond_wait(&s->cond, &s->mutex) :
            pthread_cond_timedwait(&s->cond, &s->mutex, &end);
        if (rc) break;
    }
    if (!rc) --s->count;
    pthread_mutex_unlock(&s->mutex);
    return rc == ETIMEDOUT ? SDL_MUTEX_TIMEDOUT : rc ? SDL_SetError("semaphore wait: %d", rc) : 0;
}
int __wrap_SDL_SemWait(SDL_sem *s) { return __wrap_SDL_SemWaitTimeout(s, SDL_MUTEX_MAXWAIT); }
int __wrap_SDL_SemTryWait(SDL_sem *s) { return __wrap_SDL_SemWaitTimeout(s, 0); }
int __wrap_SDL_SemPost(SDL_sem *s) {
    if (!s) return SDL_SetError("NULL semaphore");
    pthread_mutex_lock(&s->mutex);
    if (s->count == UINT32_MAX) { pthread_mutex_unlock(&s->mutex); return SDL_SetError("semaphore overflow"); }
    ++s->count;
    pthread_cond_signal(&s->cond);
    pthread_mutex_unlock(&s->mutex);
    return 0;
}
Uint32 __wrap_SDL_SemValue(SDL_sem *s) {
    if (!s) return 0;
    pthread_mutex_lock(&s->mutex);
    Uint32 count = s->count;
    pthread_mutex_unlock(&s->mutex);
    return count;
}
