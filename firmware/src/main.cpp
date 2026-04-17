#include <Arduino.h>
#include "display.h"

void setup() {
    Serial.begin(115200);
    displaySetup();
    showDisplay(DisplayState::SMILE);  // D-08: power-up default = SMILE (closed eyes)
}

void loop() {
    // D-01: blocking readStringUntil — loop does nothing else, blocking is fine
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // D-03: exact string match after trim
    if (cmd == "DEFAULT") {
        showDisplay(DisplayState::OPEN_EYES);
    } else if (cmd == "SMILE") {
        showDisplay(DisplayState::SMILE);
    }
    // Unknown commands silently ignored
}
