#pragma once
#include <SDL_opengl.h>
#ifdef __cplusplus
extern "C" {
#endif
GLint gluBuild2DMipmaps(GLenum, GLint, GLsizei, GLsizei, GLenum, GLenum, const void *);
void gluPerspective(GLdouble, GLdouble, GLdouble, GLdouble);
#ifdef __cplusplus
}
#endif
