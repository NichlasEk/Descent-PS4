/* Build-time ASCII glyph atlas. The font and its OFL are shipped separately. */
#include <ft2build.h>
#include FT_FREETYPE_H
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static unsigned char pixels[512 * 288 * 4];
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    FT_Library lib; FT_Face face;
    if (FT_Init_FreeType(&lib) || FT_New_Face(lib, argv[1], 0, &face) ||
        FT_Set_Pixel_Sizes(face, 0, 28)) return 3;
    uint8_t widths[96] = {0};
    for (unsigned c = 32; c < 128; ++c) {
        if (FT_Load_Char(face, c, FT_LOAD_RENDER)) return 4;
        FT_GlyphSlot g = face->glyph;
        widths[c-32] = (g->advance.x + 32) >> 6;
        for (unsigned y = 0; y < g->bitmap.rows; ++y)
            for (unsigned x = 0; x < g->bitmap.width; ++x) {
                int dx = 2 + g->bitmap_left + x, dy = 35 - g->bitmap_top + y;
                if (dx < 0 || dx >= 32 || dy < 0 || dy >= 48) continue;
                unsigned at = (((c-32)/16*48+dy)*512+(c-32)%16*32+dx)*4;
                pixels[at] = pixels[at+1] = pixels[at+2] = 255;
                pixels[at+3] = g->bitmap.buffer[y*g->bitmap.pitch+x];
            }
    }
    FILE *out = fopen(argv[2], "wb");
    if (!out) return 6;
    int ok = fwrite(widths, 1, sizeof(widths), out) == sizeof(widths) &&
        fwrite(pixels, 1, sizeof(pixels), out) == sizeof(pixels);
    if (fclose(out)) ok = 0;
    FT_Done_Face(face); FT_Done_FreeType(lib);
    return ok ? 0 : 7;
}
