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
   
   **Windows (PowerShell)**:
   ```cmd
   .venv\Scripts\activate
   $env:PYTHONPATH="."; python app/main.py
   ```

4. **Cleanup (Optional)**:
   To remove the virtual environment and build artifacts:
   - **Windows**: Run `cleanup.bat`
   - **Linux/Mac**: Run `chmod +x cleanup.sh && ./cleanup.sh`

3. **Build Executable**:
   ```bash
   pyinstaller app.spec
   ```

## Troubleshooting

**Qt xcb error (Linux)**:
If you see `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`, it means you are running in a headless environment (no monitor) or missing libraries (`libxcb-cursor0`).
- **Solution**: This app requires a graphical desktop environment.
- **Testing**: Use `python verify_headless.py` to check the logic without GUI.

**Visual C++ 14.0 error (Windows)**:
If `pip install` fails with `Microsoft Visual C++ 14.0 or greater is required`, you are missing the C++ compiler needed for `insightface`.
- **Solution 1 (Installer)**: Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
  - Download and run the installer.
  - Select the **"Desktop development with C++"** workload.
  - Install.
- **Solution 2 (WinGet)**:
  ```cmd
  winget install -e --id Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
  ```
  *(Note: This installs the check-boxed C++ workload automatically)*
- **After installation**: Restart your terminal and run `pip install -r requirements.txt` again.

## Disclaimer
This application provides a **pre-assessment** only. The final decision on passport photo acceptance lies with the issuing authority. For German ID cards (since May 2025), purely digital submission paths may be required.

## License
AGPL-3.0
