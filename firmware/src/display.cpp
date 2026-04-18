#include <U8g2lib.h>
#include "display.h"
#include "bitmaps.h"

// Two-page buffer variant (256 bytes each vs 1024 for full-buffer) — required on UNO
// Two F-buffer instances exceed UNO's 2KB SRAM; 2-page solves silently-blank D2.

// Display 1: Hardware I2C on A4 (SDA) / A5 (SCL)
// Physical CCW 90° → U8G2_R1 corrects to portrait (64w × 128h canvas)
U8G2_SSD1306_128X64_NONAME_2_HW_I2C u8g2_hw(U8G2_R1, U8X8_PIN_NONE);

// Display 2: Software I2C on A2 (SDA=16) / A3 (SCL=17)
// Physical CW 90° → U8G2_R3 corrects to portrait (64w × 128h canvas)
U8G2_SSD1306_128X64_NONAME_2_SW_I2C u8g2_sw(U8G2_R3, /*clock=*/17, /*data=*/16, U8X8_PIN_NONE);

void displaySetup() {
    bool hw_ok = u8g2_hw.begin();
    bool sw_ok = u8g2_sw.begin();
    Serial.begin(115200);
    Serial.print("HW I2C (A4/A5): "); Serial.println(hw_ok ? "OK" : "FAIL");
    Serial.print("SW I2C (A2/A3): "); Serial.println(sw_ok ? "OK" : "FAIL");
}

void showDisplay(DisplayState state) {
    const uint8_t* bmp;
    if (state == DisplayState::OPEN_EYES) {
        bmp = open_eyes_bits;
    } else if (state == DisplayState::SMILE) {
        bmp = smile_bits;
    } else {
        bmp = angry_bits;
    }

    u8g2_hw.firstPage();
    do {
        u8g2_hw.drawXBMP(0, 0, 64, 128, bmp);
    } while (u8g2_hw.nextPage());

    u8g2_sw.firstPage();
    do {
        u8g2_sw.drawXBMP(0, 0, 64, 128, bmp);
    } while (u8g2_sw.nextPage());
}
