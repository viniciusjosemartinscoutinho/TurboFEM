#. 'C:\Users\ucfil\Desktop\desktop\codes\ps1\reset-drivers\vinicius-packages.ps1'

#Start-Process Powershell -ArgumentList "C:\Users\ucfil\Desktop\desktop\codes\ps1\reset-drivers\vinicius-packages.ps1" #paralelo

$python = "C:/Program Files/Python311/python.exe"

Write-Host "Installing packages..." -ForegroundColor Cyan


# List
$packages = @(
    "PIL",
    "pyinstaller",
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "reportlab",
    "graphviz",
    "pikepdf",
    "argostranslate",
    "argostranslate.package",
    "argostranslate.translate",
    "langdetect",
    "webdriver-manager selenium",
    "ChromeDriverManager",
    "webdriver_manager.chrome",
    "undetected_chromedriver",
    "webdriver-manager selenium",
    "requests",
    "PyPDF2",
    "socket",
    "speedtest-cli",
    "uuid",
    "tectonic",
    "tempfile",
    "spacy.lang.fr.stop_words",
    "spacy",
    "concurrent",
    "hashlib",
    "datetime",
    "python-pptx",
    "joblib",
    "protonvpn-cli",
    "deep_translator",
    "accelerate>=0.26.0",
    "sentencepiece",
    "tf-keras",
    "datasets",
    "sentence_transformers",
    "imblearn",
    "io",
    "tokenize",
    "urllib.request",
    "yt_dlp",
    "msal requests",
    "msal",
    "requests",
    "py7zr",
    "glob",
    "json",
    "subprocess",
    "whisper",
    "pyannote",
    "openai",
    "dotenv" 
    "seaborn",
    "pywin32",
    "openpyxl",
    "pyperclip",
    "shutil",
    "os",
    "time",
    "random",
    "psutil",
    "spacy",
    "pandas",
    "requests",
    "matplotlib",
    "xlrd",
    "python-docx",
    "pyautogui",
    "keyboard",
    "pyperclip",
    "pynput",
    "tensorflow",
    "keras",
    "opencv-python",
    "scikit-learn",
    "numpy",
    "pyttsx3",
    "pillow",
    "beautifulsoup4",
    "lxml",
    "selenium"
)

foreach ($pkg in $packages) {
    Write-Host " - Installing: $pkg"
    & $python -m pip install --user $pkg
}


Write-Host "Done."


