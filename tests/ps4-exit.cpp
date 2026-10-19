#include <orbis/SystemService.h>
#include <fcntl.h>
#include <unistd.h>

// Reached from libc _Exit only AFTER normal exit handlers and stdio cleanup.
// Use file descriptors here: stdio shutdown has already run.
static void marker(const char *text, unsigned length) {
    const int fd = open("/data/descent-ps4/runtime-probe.log", O_WRONLY | O_APPEND);
    if (fd >= 0) {
        write(fd, text, length);
        close(fd);
    }
}
extern "C" [[noreturn]] void __real__exit(int status);
extern "C" [[noreturn]] void __wrap__exit(int status) {
    constexpr char reached[] = "PASS: libc cleanup complete; requesting PS4 system exit\n";
    marker(reached, sizeof(reached) - 1);
    const int result = sceSystemServiceLoadExec("exit", nullptr);
    if (result < 0) {
        constexpr char failed[] = "FAIL: PS4 system exit rejected; falling back to kernel exit\n";
        marker(failed, sizeof(failed) - 1);
        __real__exit(status);
    }
    // Successful request is asynchronous; do not fall back while it completes.
    for (;;) sleep(1);
}
