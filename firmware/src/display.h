#pragma once

enum class DisplayState {
    OPEN_EYES,
    SMILE,
    ANGRY
};

void displaySetup();
void showDisplay(DisplayState state);
