// Upstream uses these C++20/23 library facilities throughout the engine.
#include <ranges>
#include <span>
#include <array>
int main() {
    std::array<int, 3> values{1, 2, 3};
    std::span<int> view(values);
    int total = 0;
    for (int value : view | std::views::reverse) total += value;
    return total == 6 ? 0 : 1;
}
