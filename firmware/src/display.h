#pragma once

enum class DisplayState {
    OPEN_EYES,
    SMILE
};

void displaySetup();
void showDisplay(DisplayState state);
