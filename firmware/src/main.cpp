#include <Arduino.h>
#include "display.h"

void setup() {
    Serial.begin(115200);
    displaySetup();
    showDisplay(DisplayState::OPEN_EYES);
}

void loop() {
    showDisplay(DisplayState::OPEN_EYES);
    delay(2000);
    showDisplay(DisplayState::SMILE);
    delay(2000);
}
