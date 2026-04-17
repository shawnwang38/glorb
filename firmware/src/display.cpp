#include <U8g2lib.h>
#include "display.h"

// U8G2_R2 rotates the display 180 degrees, compensating for the
// upside-down physical mount of the SSD1306 OLED. No manual bitmap
// flipping is required — the rotation constructor handles it.
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R2, U8X8_PIN_NONE);

void displaySetup() {
    u8g2.begin();
}

void showDisplay(DisplayState state) {
    u8g2.clearBuffer();

    switch (state) {
        case DisplayState::OPEN_EYES:
            u8g2.setDrawColor(1);
            // Left eye: 40px wide, 8px tall, starting at (14, 28)
            u8g2.drawBox(14, 28, 40, 8);
            // Right eye: 40px wide, 8px tall, starting at (74, 28)
            u8g2.drawBox(74, 28, 40, 8);
            break;

        case DisplayState::SMILE:
            u8g2.setFont(u8g2_font_logisoso32_tr);
            // ">" on the left side, "<" on the right side — forms a smile
            u8g2.drawStr(8, 50, ">");
            u8g2.drawStr(78, 50, "<");
            break;
    }

    u8g2.sendBuffer();
}
