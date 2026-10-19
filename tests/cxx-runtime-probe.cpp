#include <locale>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <cstdio>
#include <sys/stat.h>

int main() {
    mkdir("/data/descent-ps4", 0777);
    auto *log = std::fopen("/data/descent-ps4/runtime-probe.log", "w");
    if (!log) return 2;
    std::setvbuf(log, nullptr, _IONBF, 0);
    std::fprintf(log, "START: runtime probe only, not the game\n");
    try {
    int result = 0;
    std::thread worker([&] { result = 42; });
    worker.join();
    std::fprintf(log, "PASS: thread join, result=%d\n", result);
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << result;
    std::fprintf(log, "PASS: classic locale and stringstream\n");
    try {
        throw std::runtime_error(output.str());
    } catch (const std::exception &error) {
        std::printf("Descent runtime probe: %s\n", error.what());
        std::fprintf(log, "PASS: exception caught: %s\nRESULT: %s\n", error.what(),
                     output.str() == "42" ? "PASS" : "FAIL");
        std::fclose(log);
        return output.str() == "42" ? 0 : 1;
    }
    } catch (const std::exception &error) {
        std::fprintf(log, "FAIL: %s\n", error.what());
        std::fclose(log);
        return 1;
    }
}
