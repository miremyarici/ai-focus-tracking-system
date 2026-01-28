# Focus Tracker

This project is a real-time attention monitoring system developed using Python and OpenCV. It utilizes computer vision techniques to analyze the user's eye movements and gaze direction via a webcam. The system detects when the user looks away from the screen or loses focus and provides audio-visual alerts to help maintain attention.

## Features

* **Real-time Eye Tracking:** Uses Haar Cascade classifiers to detect faces and eyes efficiently.
* **Gaze Direction Analysis:** Estimates whether the user is looking at the center, left, or right based on the pupil's position relative to the eye.
* **Lighting Adaptation:** The `GazeDetector` module implements Histogram Equalization and Dynamic Thresholding to ensure accuracy in various lighting conditions (low light/bright environments).
* **Distraction Alerts:** The `AlertManager` triggers an audio warning if the user does not look at the screen for a specified duration.
* **Cross-Platform Support:** Designed to run on Windows, macOS, and Linux (audio output adapts to the OS).
* **Customizable Settings:** Sensitivity, timer durations, and audio preferences can be adjusted via `config.py`.

## Installation

Follow these steps to set up the project on your local machine.

### Requirements
Ensure you have Python 3.x installed along with the following libraries:

* OpenCV (`cv2`)
* NumPy
* Pygame (for audio alerts)

### Setup

1. Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/ai-focus-tracking-system.git](https://github.com/yourusername/ai-focus-tracking-system.git)
    cd ai-focus-tracking-system
    ```

2. Install the required dependencies:
    ```bash
    pip install opencv-python numpy pygame
    ```

## Usage

1. Ensure your webcam is connected.
2. Run the main script:
    ```bash
    python main.py
    ```
3. When the application starts, position your face in the center of the camera frame.
4. The system will display your current gaze direction (Center, Left, Right) on the screen.
5. If you look away from the screen for the duration defined in the settings, an alert will sound.

## Configuration

You can modify the system behavior by editing the `config.py` file:

* **GAZE_SENSITIVITY:** Adjusts the threshold for detecting eye movement.
* **TIME_OPTIONS:** Sets the focus and break durations.
* **ALERT_COOLDOWN:** The time interval between consecutive alerts.
* **SOUND_FILE:** Path to the alert sound file.

## Project Structure

* `alert_manager.py`: Handles audio and visual alerts in a thread-safe manner.
* `gaze_detector.py`: The core module for image processing, face/eye detection, and gaze estimation.
* `config.py`: Contains configuration variables for colors, resolution, and sensitivity settings.

## Contributing

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Added new feature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.
