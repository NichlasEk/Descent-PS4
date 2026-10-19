/* Descent's legacy GL requests on the single-backbuffer PS4GL renderer.
 * Initial quality limits: base-level textures, one-pixel lines/points, no stereo.
 */
#include "ps4gl.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static void invalid(GLenum value) {
    PS4GLContext *c = ps4glCurrentContext();
    if (c && !c->error) c->error = value;
}
extern void __real_glDrawArrays(GLenum, GLint, GLsizei);
void __wrap_glDrawArrays(GLenum mode, GLint first, GLsizei count) {
    /* PS4GL's legacy client arrays accept triangles/quads. Preserve strip
     * winding and fan topology by indexing the original client arrays. */
    if (mode != 0x0005 /* TRIANGLE_STRIP */ && mode != 0x0006 /* TRIANGLE_FAN */) {
        __real_glDrawArrays(mode, first, count); return;
    }
    if (first < 0 || count < 0) { invalid(GL_INVALID_VALUE); return; }
    if (count < 3) return;
    if ((size_t)count > PS4GL_MAX_BUFFER_BYTES / (3 * sizeof(GLuint))) { invalid(GL_OUT_OF_MEMORY); return; }
    GLuint *indices = malloc((size_t)(count - 2) * 3 * sizeof(*indices));
    if (!indices) { invalid(GL_OUT_OF_MEMORY); return; }
    for (GLsizei i = 0; i < count - 2; ++i) {
        indices[i*3] = (GLuint)first + (mode == 0x0006 ? 0 : i + (i & 1));
        indices[i*3+1] = (GLuint)first + (mode == 0x0006 ? i + 1 : i + 1 - (i & 1));
        indices[i*3+2] = (GLuint)first + i + 2;
    }
    PS4GLContext *c = ps4glCurrentContext();
    GLuint previous = c ? c->element_buffer : 0;
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
    glDrawElements(GL_TRIANGLES, (count - 2) * 3, GL_UNSIGNED_INT, indices);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, previous);
    free(indices);
}
void glDrawBuffer(GLenum buffer) {
    if (buffer != 0x0405 /* BACK */ && buffer != 0x0402 /* BACK_LEFT */)
        invalid(GL_INVALID_ENUM);
}
void glReadBuffer(GLenum buffer) { glDrawBuffer(buffer); }
void glLineWidth(GLfloat width) {
    if (width <= 0) invalid(GL_INVALID_VALUE);
    // Backend supports width 1; larger requested widths are clamped.
}
void glPointSize(GLfloat size) {
    if (size <= 0) invalid(GL_INVALID_VALUE);
}
void glPrioritizeTextures(GLsizei count, const GLuint *textures, const GLfloat *priorities) {
    (void)textures; (void)priorities; // Optional residency hint; all textures resident.
    if (count < 0) invalid(GL_INVALID_VALUE);
}
void glTexParameterf(GLenum target, GLenum pname, GLfloat value) {
    if (pname == 0x84fe /* MAX_ANISOTROPY_EXT */) {
        if (value != 1.0f) invalid(GL_INVALID_VALUE);
        return;
    }
    glTexParameteri(target, pname, (GLint)value);
}
void glGetTexLevelParameteriv(GLenum target, GLint level, GLenum pname, GLint *value) {
    PS4GLContext *c = ps4glCurrentContext();
    if (!value) return;
    *value = 0;
    if (!c || target != GL_TEXTURE_2D || level != 0) { invalid(GL_INVALID_VALUE); return; }
    GLuint name = c->texture_bindings[c->active_texture];
    PS4GLTexture *t = NULL;
    for (unsigned i = 0; i < PS4GL_MAX_TEXTURES; ++i)
        if (c->textures[i].created && c->textures[i].name == name) { t = &c->textures[i]; break; }
    if (!t) return;
    switch (pname) {
    case 0x1000: *value = t->width; break;
    case 0x1001: *value = t->height; break;
    case 0x805c: case 0x805d: case 0x805e: case 0x805f: *value = 8; break;
    case 0x8060: case 0x8061: break; // Normalized to RGBA8, no separate L/I storage.
    default: invalid(GL_INVALID_ENUM);
    }
}
void gluPerspective(double fovy, double aspect, double near_value, double far_value) {
    double top = near_value * tan(fovy * 0.008726646259971648);
    if (aspect <= 0 || top <= 0 || near_value <= 0 || far_value <= near_value) {
        invalid(GL_INVALID_VALUE); return;
    }
    GLfloat matrix[16] = {0};
    matrix[0] = near_value / (top * aspect);
    matrix[5] = near_value / top;
    matrix[10] = -(far_value + near_value) / (far_value - near_value);
    matrix[11] = -1;
    matrix[14] = -(2 * far_value * near_value) / (far_value - near_value);
    PS4GLContext *c = ps4glCurrentContext();
    if (!c) return;
    GLfloat *left = c->fixed.matrix[c->fixed.matrix_mode][c->fixed.top[c->fixed.matrix_mode]];
    GLfloat product[16] = {0};
    for (unsigned col = 0; col < 4; ++col)
        for (unsigned row = 0; row < 4; ++row)
            for (unsigned k = 0; k < 4; ++k)
                product[col*4+row] += left[k*4+row] * matrix[col*4+k];
    glLoadMatrixf(product);
}
extern void descent_finish_frame(void);
void glFinish(void) { descent_finish_frame(); }
