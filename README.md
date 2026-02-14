# PassPhotoCheck

![PassPhotoCheck Logo](images/logo.png)

A portable Windows desktop application for biometric passport photo analysis, strictly following DE/BMI and ICAO/ISO standards.

## Features
- **Offline Operation**: Privacy-first, no cloud dependencies.
- **Biometric Checks**: Geometry (head size, eye position), expression, and quality.
- **Standards Compliance**: Verification based on ICAO 9303 & ISO/IEC 29794-5.
- **Portable**: runs as a single executable or folder.

## Setup & Running (Dev)

1. **Install Dependencies**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Application**:
   
   **Linux/Mac**:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   **Windows**:
   ```cmd
   run.bat
   ```

3. **Build Executable**:
   ```bash
   pyinstaller app.spec
   ```

## Troubleshooting

**Qt xcb error (Linux)**:
If you see `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`, it means you are running in a headless environment (no monitor) or missing libraries (`libxcb-cursor0`).
- **Solution**: This app requires a graphical desktop environment.
- **Testing**: Use `python verify_headless.py` to check the logic without GUI.

## Disclaimer
This application provides a **pre-assessment** only. The final decision on passport photo acceptance lies with the issuing authority. For German ID cards (since May 2025), purely digital submission paths may be required.

## License
MIT
