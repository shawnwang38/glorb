#include <U8g2lib.h>
#include "display.h"

// Two-page buffer variant (256 bytes each vs 1024 for full-buffer) — required on UNO
// Two F-buffer instances exceed UNO's 2KB SRAM; 2-page solves silently-blank D2.

// Display 1: Hardware I2C on A4 (SDA) / A5 (SCL)
// Physical CCW 90° → U8G2_R1 corrects to portrait (64w × 128h canvas)
U8G2_SSD1306_128X64_NONAME_2_HW_I2C u8g2_hw(U8G2_R1, U8X8_PIN_NONE);

// Display 2: Software I2C on A2 (SDA=16) / A3 (SCL=17)
// Physical CW 90° → U8G2_R3 corrects to portrait (64w × 128h canvas)
U8G2_SSD1306_128X64_NONAME_2_SW_I2C u8g2_sw(U8G2_R3, /*clock=*/17, /*data=*/16, U8X8_PIN_NONE);

static void drawEyePage(U8G2 &u8g2) {
    // D-05: outline only (drawEllipse not drawFilledEllipse) — dark center, lit ring
    u8g2.setDrawColor(1);
    u8g2.drawEllipse(32, 64, 20, 30, U8G2_DRAW_ALL);
}

static void drawSmilePage(U8G2 &u8g2) {
    // D-06: upper arc of ellipse — upper ~30% of ellipse outline = ^ arc shape
    // rx=20 matches OPEN_EYES width; ry=10 gives gentle curve; cy=72 centers on canvas
    u8g2.setDrawColor(1);
    u8g2.drawEllipse(32, 72, 20, 10, U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT);
}

void displaySetup() {
    u8g2_hw.begin();
    u8g2_sw.begin();
}

void showDisplay(DisplayState state) {
    typedef void (*DrawFn)(U8G2 &);
    DrawFn fn = (state == DisplayState::OPEN_EYES) ? drawEyePage : drawSmilePage;

    u8g2_hw.firstPage();
    do { fn(u8g2_hw); } while (u8g2_hw.nextPage());

    u8g2_sw.firstPage();
    do { fn(u8g2_sw); } while (u8g2_sw.nextPage());
}
