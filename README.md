#Breeze PDF Viewer

A modern and stylish PDF viewer built with Python, utilizing CustomTkinter for a sleek user interface, PyMuPDF (fitz) for robust PDF handling, and Pillow for image processing. Breeze PDF Viewer offers essential functionalities for comfortable PDF document viewing.

✨ Features
Clean and Modern UI: Powered by CustomTkinter, providing a visually appealing and intuitive user experience with support for system-wide light and dark modes.

PDF Viewing: Open and display PDF documents effortlessly.

Navigation: Easily navigate through pages using next/previous buttons, page number input, or mouse wheel scrolling.

Zoom Functionality: Zoom in and out of documents for detailed viewing or a broader overview.

Page Rotation: Rotate pages by 90 degrees for better readability.

Printing: Print the current page directly from the application (requires a configured default PDF viewer/printer on your system).

Responsive Design: Adapts to window resizing, ensuring the PDF content remains viewable.

Keyboard Shortcuts: Quick access to common functions like opening files, zooming, and page navigation.

🚀 Technologies Used
Python 3.x

CustomTkinter: For modern GUI elements and theme management.

PyMuPDF (fitz): High-performance PDF rendering and manipulation.

Pillow (PIL): Image processing library for converting PDF pages to displayable images.

CTkMessagebox: Custom message boxes for better UI consistency.

🖥️ Installation and Setup
Prerequisites
Python 3.7+

pip (Python package installer)

Steps
Clone the repository:

git clone https://github.com/your-username/breeze-pdf-viewer.git
cd breeze-pdf-viewer

(Replace your-username with your actual GitHub username.)

Create a virtual environment (recommended):

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Install dependencies:

pip install customtkinter PyMuPDF Pillow CTkMessagebox

Prepare Icons:
The application uses specific icons for the toolbar and the main application window.

Application Icon (app_icon.ico): Place your main application icon (in .ico format) in the root directory of the project.

Toolbar Icons: Create an icons subdirectory in the root of your project. Inside this folder, place PNG images for light and dark modes (e.g., open_pdf_light.png, open_pdf_dark.png). These should be 32x32 pixels.

Your project structure should look like this:

breeze-pdf-viewer/
├── pdf_viewer_app.py
├── app_icon.ico
└── icons/
    ├── open_pdf_light.png
    ├── open_pdf_dark.png
    ├── zoom_in_light.png
    ├── zoom_in_dark.png
    └── ... (other required icons)

▶️ How to Run
After setting up, simply run the main Python script:

python pdf_viewer_app.py

📦 Building an Executable (Windows)
You can use PyInstaller to create a standalone executable file (.exe) for easier distribution.

Install PyInstaller:

pip install pyinstaller

Build the executable:
Navigate to your project's root directory in the terminal and run:

pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "icons;icons" pdf_viewer_app.py

--noconsole: Prevents a console window from appearing when the app runs.

--onefile: Creates a single executable file.

--icon=app_icon.ico: Sets the icon for the generated .exe file.

--add-data "icons;icons": Includes the icons directory within the executable. The first icons is the source path, and the second icons is the destination inside the executable.

Locate the executable:
The executable will be generated in the dist/ directory within your project folder.

🤝 Contributing
Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, feel free to open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License.
(Create a LICENSE file in your repository with the MIT License text, or link to another suitable license.)
