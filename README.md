# HandLaunch

A desktop application that uses hand gesture recognition to launch applications via camera input.

## Features

- **Real-time Hand Gesture Recognition**: Uses MediaPipe and OpenCV for accurate hand tracking
- **Customizable Gesture Mapping**: Map any gesture to any application
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **User-friendly Interface**: Intuitive PyQt6 GUI for easy setup and management
- **Gesture Training**: Train custom gestures for personalized control

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam or built-in camera
- 4GB RAM minimum (8GB recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HandLaunch.git
cd HandLaunch
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Usage

1. **Setup**: Launch the app and allow camera access
2. **Train Gestures**: Use the gesture trainer to record your custom gestures
3. **Map Applications**: Assign gestures to specific applications
4. **Start Gesturing**: Make gestures in front of the camera to launch apps!

## Supported Gestures

- Open Palm
- Fist
- Peace Sign (V)
- Thumbs Up
- Pointing
- Custom gestures (user-defined)

## Configuration

The application stores configuration in `data/config/user_config.json`. You can:
- Modify gesture sensitivity
- Change camera settings
- Add/remove gesture mappings
- Configure startup behavior

## Development

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for detailed development instructions.

## Packaging

Build cross-platform binaries with PyInstaller:

```bash
python scripts/build.py --target all --clean
```

Artifacts will be generated under `dist/`. Copy or link the latest ones to `website/downloads/` to update the download page, or point the links to GitHub Releases.

## Website

Static site is in `website/`. It detects the visitor OS and highlights the correct download.

To deploy on Vercel, push to the repository with `vercel.json` present. The routes map `/` to `website/index.html`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe for hand detection capabilities
- OpenCV for computer vision processing
- PyQt5 for the desktop interface

