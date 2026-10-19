#include <locale>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <cstdio>
#include <cstdlib>
#include <sys/stat.h>

static constexpr auto log_path = "/data/descent-ps4/runtime-probe.log";
static void append(const char *message) {
    if (auto *log = std::fopen(log_path, "a")) {
        std::fprintf(log, "%s\n", message);
        std::fclose(log);
    }
}
static void at_exit_marker() { append("PASS: atexit callback"); }
__attribute__((destructor)) static void finalizer_marker() {
    append("PASS: fini_array callback; returning to libc shutdown");
}

static int run_tests(FILE *log) {
    int result = 0;
    std::thread worker([&] { result = 42; });
    worker.join();
    std::fprintf(log, "PASS: thread join, result=%d\n", result);
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << result;
    std::fprintf(log, "PASS: classic locale and stringstream\n");
    bool caught = false;
    try {
        throw std::runtime_error(output.str());
    } catch (const std::exception &error) {
        std::fprintf(log, "PASS: exception caught: %s\n", error.what());
        caught = true;
    }
    std::fprintf(log, "PASS: exception destroyed; leaving local object scope\n");
    return caught && output.str() == "42" ? 0 : 1;
}

int main() {
    mkdir("/data/descent-ps4", 0777);
    auto *log = std::fopen(log_path, "w");
    if (!log) return 2;
    std::setvbuf(log, nullptr, _IONBF, 0);
    std::fprintf(log, "START: runtime probe 0.03, not the game\n");
    if (std::atexit(at_exit_marker) != 0) {
        std::fprintf(log, "FAIL: atexit registration\n");
        std::fclose(log);
        return 3;
    }
    int status = 1;
    try {
        status = run_tests(log);
        std::fprintf(log, "PASS: local objects destroyed\n");
    } catch (const std::exception &error) {
        std::fprintf(log, "FAIL: %s\n", error.what());
    }
    std::fprintf(log, "RESULT: %s\n", status == 0 ? "PASS" : "FAIL");
    std::fclose(log);
    append("PASS: log closed; returning from main");
    return status;
}
