#include <U8g2lib.h>
#include "display.h"

// Display 1: Hardware I2C on A4 (SDA) / A5 (SCL)
// Physical mount is CCW 90° rotated — U8G2_R1 corrects to portrait (64w x 128h canvas)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2_hw(U8G2_R1, U8X8_PIN_NONE);

// Display 2: Software I2C on A2 (SDA=16) / A3 (SCL=17)
// Physical mount is CW 90° rotated — U8G2_R3 corrects to portrait (64w x 128h canvas)
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2_sw(U8G2_R3, /*clock=*/17, /*data=*/16, U8X8_PIN_NONE);

// Draw OPEN_EYES state to one U8g2 instance.
// Portrait canvas: 64px wide x 128px tall after rotation correction.
// Filled ellipse centered at (32, 64), rx=20, ry=30.
static void drawEye(U8G2 &u8g2) {
    u8g2.setDrawColor(1);
    // cx=32, cy=64, rx=20 (horizontal radius), ry=30 (vertical radius)
    u8g2.drawFilledEllipse(32, 64, 20, 30, U8G2_DRAW_ALL);
}

// Draw SMILE state to one U8g2 instance.
// "^" character with logisoso32 font, centered on 64x128 portrait canvas.
static void drawSmile(U8G2 &u8g2) {
    u8g2.setFont(u8g2_font_logisoso32_tr);
    // "^" rendered: character width ~24px, height ~32px
    // Centered: x = (64 - charW) / 2, y = 80 (baseline below center)
    int charW = u8g2.getStrWidth("^");
    int x = (64 - charW) / 2;
    int y = 80;  // baseline position on 128px tall canvas
    u8g2.drawStr(x, y, "^");
}

void displaySetup() {
    u8g2_hw.begin();
    u8g2_sw.begin();
}

void showDisplay(DisplayState state) {
    // Update both displays in one call
    switch (state) {
        case DisplayState::OPEN_EYES:
            u8g2_hw.clearBuffer();
            drawEye(u8g2_hw);
            u8g2_hw.sendBuffer();

            u8g2_sw.clearBuffer();
            drawEye(u8g2_sw);
            u8g2_sw.sendBuffer();
            break;

        case DisplayState::SMILE:
            u8g2_hw.clearBuffer();
            drawSmile(u8g2_hw);
            u8g2_hw.sendBuffer();

            u8g2_sw.clearBuffer();
            drawSmile(u8g2_sw);
            u8g2_sw.sendBuffer();
            break;
    }
}
