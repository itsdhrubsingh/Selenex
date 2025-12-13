<p align="center">
  <img src="selenex-recorder/icons/icon.png" alt="SeleneX Logo" width="128"/>
</p>

# SeleneX

SeleneX is a lightweight Selenium automation recorder designed to help testers and SDETs accelerate test creation.

It records real user interactions (clicks, inputs, scrolling, navigation) and converts them into stable, readable Selenium Python scripts using heuristic-based selector selection instead of brittle XPath-only approaches.

SeleneX is framework-agnostic and intentionally leaves test architecture, assertions, and POM design to the automation engineer.

## Features

-   **Robust Selectors**: Uses a smart heuristic engine to find stable selectors (ID, TestID, Name, Semantic Text) and falls back to parent-chain logic for difficult elements.
-   **Smart Waits**: Automatically implements `WebDriverWait` (dynamic waits) instead of hard sleeps for maximum speed and stability.
-   **Multi-Page Support**: Detects URL changes and automatically inserts navigation waits.
-   **Element Handling**: Intelligently handles complex inputs like Dropdowns (`<select>`), Radio Buttons, and Checkboxes.
-   **Resilient Actions**: Uses `ActionChains` and JavaScript fallbacks to ensure clicks work even on overlay-heavy modern web apps.

## Prerequisites

1.  **Python 3.x** installed.
2.  **Chrome Browser** installed.
3.  **Selenium** library:
    ```bash
    pip install selenium
    ```

## Installation

1.  **Load the Extension**:
    -   Open Chrome and go to `chrome://extensions`.
    -   Enable **Developer mode** (top right).
    -   Click **Load unpacked**.
    -   Select the `selenex-recorder` folder from this project.

2.  **Prepare the Generator**:
    -   Ensure `generator.py` is in your project folder.

## Usage

### 1. Record a Session
1.  Click the extension icon in Chrome.
2.  Click **Start Recording**.
3.  Interact with the website (Click, Type, Scroll, Navigate).
4.  Click **Stop Recording**.
5.  Click **Download Session** to save `session.json`.

### 2. Generate Script
Run the generator with your session file:

```bash
python generator.py session.json
```

This will create `test_script.py`.

### 3. Run Test
Execute the generated Python script:

```bash
python test_script.py
```

## Project Structure

-   `ai-recorder/`: Source code for the Chrome Extension.
-   `generator.py`: Core logic that parses `session.json` and produces Selenium code.
-   `session.json`: The raw data captured by the recorder.
-   `test_script.py`: The output executable Selenium script.

## Troubleshooting

-   **Invalid Element State**: If you see this, ensure you are using the latest `generator.py`, which correctly handles non-text inputs (Radios/Selects).
-   **Element Not Clickable**: The script uses `ActionChains` to mitigate this. If it persists, check if the element is permanently covered by another UI element.
