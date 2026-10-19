#!/usr/bin/env python3
"""Compile the actual patched lookup against a mocked legacy hash boundary."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root / 'engine/similar/main/piggy.cpp').read_text()
start = source.index('int piggy_find_sound(const std::span<const char> name)')
end = source.index('\n}', start) + 2
test = r'''
#include <array>
#include <span>
#include <cstring>
#include <cassert>
static int AllDigiSndNames;
static int hashtable_search(int *, const char *name) {
    return std::strcmp(name, "laser03") == 0 ? 42 : -1;
}
''' + source[start:end] + r'''
int main() {
    const char full[] = "laser03.raw";
    assert(piggy_find_sound(std::span(full, 7)) == 42);
    const std::array<char, 7> bare{'l','a','s','e','r','0','3'};
    assert(piggy_find_sound(bare) == 42);
    assert(piggy_find_sound(std::span(full, 11)) == 255);
    assert(piggy_find_sound({}) == 255);
    const std::array<char, 32> oversized{};
    assert(piggy_find_sound(oversized) == 255);
}
'''
binary = root / 'build/test-sound-span'
subprocess.run(['g++','-std=c++20','-fsanitize=address,undefined','-fno-sanitize-recover=all','-x','c++','-',
                '-o',str(binary)], input=test, text=True, check=True)
subprocess.run([str(binary)], check=True)
print('PASS actual sound lookup: basename span, non-NUL input, full name, empty, oversized')
