#include <locale>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <cstdio>

int main() {
    int result = 0;
    std::thread worker([&] { result = 42; });
    worker.join();
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << result;
    try {
        throw std::runtime_error(output.str());
    } catch (const std::exception &error) {
        std::printf("Descent runtime probe: %s\n", error.what());
        return output.str() == "42" ? 0 : 1;
    }
}
