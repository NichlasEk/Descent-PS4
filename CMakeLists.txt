cmake_minimum_required(VERSION 3.20)
project(descent_ps4 LANGUAGES C CXX)
set(CMAKE_SKIP_RPATH ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 23)
set(STACK "${CMAKE_CURRENT_SOURCE_DIR}/../ScummVM-PS4")
set(NATIVE "${STACK}/.tools/opengnm-stack")
set(DEPS "${CMAKE_CURRENT_SOURCE_DIR}/build/ps4-deps")
include("${CMAKE_CURRENT_SOURCE_DIR}/build/ps4-engine/objects.cmake")
add_library(ps4_graphics STATIC)
foreach(unit ps4gl ps4gl-vulkan ps4gl-glsl ps4gl-frame ps4gl-display)
  target_sources(ps4_graphics PRIVATE "${STACK}/compat/ps4gl/${unit}.c")
endforeach()
target_include_directories(ps4_graphics PUBLIC "${STACK}/compat/ps4gl"
  "${NATIVE}/Vulkan-Headers/include" "${NATIVE}/vulkan-ps4/include" "${STACK}/.tools/glslang")
foreach(game 1 2 launcher)
  if(game STREQUAL "launcher")
    add_executable(descentlauncher platform/ps4/launcher.c platform/ps4/input.c platform/ps4/semaphore.c tests/ps4-exit.cpp)
  else()
  add_executable(descent${game} platform/ps4/main.c platform/ps4/gl-compat.c platform/ps4/audio.c platform/ps4/semaphore.c platform/ps4/input.c tests/ps4-exit.cpp
    ${DESCENT_OBJECTS_0} ${DESCENT_OBJECTS_${game}})
  target_compile_definitions(descent${game} PRIVATE DESCENT_GAME=${game})
  target_link_options(descent${game} PRIVATE "-Wl,--wrap=main")
  endif()
  target_include_directories(descent${game} PRIVATE "${DEPS}/include/c++/v1" "${OO_PS4_TOOLCHAIN}/include/SDL2")
  target_link_options(descent${game} PRIVATE -fuse-ld=lld -nostdlib
    "-Wl,-pie,--eh-frame-hdr,-z,max-page-size=0x4000"
    "-Wl,--script=${OO_PS4_TOOLCHAIN}/link.x"
    "-Wl,--script=${CMAKE_CURRENT_SOURCE_DIR}/cmake/runtime-fini.ld"
    "-Wl,--wrap=_exit,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free")
  if(NOT game STREQUAL "launcher")
    target_link_options(descent${game} PRIVATE "-Wl,--wrap=SDL_OpenAudio,--wrap=SDL_CloseAudio")
    target_link_options(descent${game} PRIVATE "-Wl,--wrap=glDrawArrays")
  endif()
  target_link_options(descent${game} PRIVATE "-Wl,--wrap=SDL_PrivateJoystickAxis")
  foreach(sem CreateSemaphore DestroySemaphore SemWaitTimeout SemWait SemTryWait SemPost SemValue)
    target_link_options(descent${game} PRIVATE "-Wl,--wrap=SDL_${sem}")
  endforeach()
  target_link_directories(descent${game} PRIVATE "${DEPS}/lib" "${OO_PS4_TOOLCHAIN}/lib")
  target_link_libraries(descent${game} PRIVATE "${OO_PS4_TOOLCHAIN}/lib/crt1.o" ps4_graphics
    "${CMAKE_CURRENT_SOURCE_DIR}/build/ps4-physfs/libphysfs.a"
    "${STACK}/build/ps4-sdlgl/libSDL2.a"
    "${OO_PS4_TOOLCHAIN}/lib/libSDL2_image.a"
    -Wl,--whole-archive "${NATIVE}/vulkan-ps4/libvulkan_ps4.a" "${NATIVE}/opengnm/libopengnm.a" -Wl,--no-whole-archive
    "${STACK}/build/scummvm-vulkan/bridge/libpsbc-scummvm.a"
    "${STACK}/build/glslang-orbis/libglslang-ps4.a"
    SceGnmDriver SceVideoOut SceUserService SceAudioOut ScePad SceMouse SceSysmodule SceNet SceSystemService
    c++ c++abi unwind c kernel)
endforeach()
