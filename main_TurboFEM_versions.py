from __future__ import annotations
#  & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\main_TurboFEM_versions.py #serie
# Start-Process "C:/Program Files/Python311/python.exe"  -ArgumentList "C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\main_TurboFEM_versions.py" #parallelism
#The "clears " are true for development but it's false just to create an ".exe" using pyinstaller 
clear = True
clearpy = True
from pathlib import Path
import shutil
import sys
import subprocess
import importlib
import importlib.metadata
#functions that clear the "keys.txt"... 
def clone_empty(txt):
    txt = Path(__file__).parent / txt

    backup = txt.with_name(f"{txt.stem}02{txt.suffix}")

    txt.replace(backup)   # sobrescreve keys02.txt se ele existir
    txt.touch()           # cria um keys.txt vazio

def v0_clone_empty(txt):
    txt = Path(txt)

    if not txt.exists():
        raise FileNotFoundError(txt)

    backup = txt.with_name(f"{txt.stem}02{txt.suffix}")

    # Renomeia o original para "...02"
    txt.rename(backup)

    # Cria um novo arquivo vazio com o nome antigo
    txt.touch()

    return txt

def clone_empty_v02(txt):
    txt = Path(txt)

    if not txt.is_absolute():
        txt = Path(__file__).parent / txt

    if not txt.exists():
        raise FileNotFoundError(txt)

    backup = txt.with_name(f"{txt.stem}02{txt.suffix}")

    txt.rename(backup)
    txt.touch()

    return txt

#anothe function that recovers "keys.txt" 
def restore_original(txt):
    txt = Path(txt)

    backup = txt.with_name(f"{txt.stem}02{txt.suffix}")

    if not backup.exists():
        raise FileNotFoundError(backup)

    # Remove o clone (vazio ou não)
    if txt.exists():
        txt.unlink()

    # Restaura o original
    backup.rename(txt)

    return txt

#another functon to create new txt
def create_empty_txt(txt):
    pasta_script = Path(__file__).parent

    arquivo = pasta_script / txt

    if arquivo.suffix != ".txt":
        arquivo = arquivo.with_suffix(".txt")

    arquivo.touch(exist_ok=True)

    return arquivo

#all packages for this project
LIBRARIES: dict[str, str] = {
    # pip package              : import name

    "pillow":                  "PIL",
    "PySide6":                 "PySide6",
    "reportlab":               "reportlab",
    "argostranslate":          "argostranslate",
    "langdetect":              "langdetect",
    "requests":                "requests",
    "speedtest-cli":           "speedtest",
    "spacy":                   "spacy",
    "joblib":                  "joblib",
    "deep-translator":         "deep_translator",
    "accelerate":              "accelerate",
    "sentencepiece":           "sentencepiece",
    "tf-keras":                "tf_keras",
    "datasets":                "datasets",
    "sentence-transformers":   "sentence_transformers",
    "yt-dlp":                  "yt_dlp",
    "msal":                    "msal",
    "py7zr":                   "py7zr",
    "python-dotenv":           "dotenv",
    "seaborn":                 "seaborn",
    "pywin32":                 "win32com",
    "pyperclip":               "pyperclip",
    "psutil":                  "psutil",
    "pandas":                  "pandas",
    "matplotlib":              "matplotlib",
    "xlrd":                    "xlrd",
    "pyautogui":               "pyautogui",
    "keyboard":                "keyboard",
    "pynput":                  "pynput",
    "tensorflow":              "tensorflow",
    "keras":                   "keras",
    "opencv-python":           "cv2",
    "scikit-learn":            "sklearn",
    "numpy":                   "numpy",
    "pyttsx3":                 "pyttsx3",
    "beautifulsoup4":          "bs4",
    "lxml":                    "lxml"    
}

#others packages...
My_LIBRARIES: dict[str, str] = {
    # pip package              : import name

    "pillow":                  "PIL",
    "PySide6":                 "PySide6",
    "reportlab":               "reportlab",
    "graphviz":                "graphviz",
    "pikepdf":                 "pikepdf",
    "argostranslate":          "argostranslate",
    "langdetect":              "langdetect",
    "webdriver-manager":       "webdriver_manager",
    "undetected-chromedriver": "undetected_chromedriver",
    "requests":                "requests",
    "PyPDF2":                  "PyPDF2",
    "speedtest-cli":           "speedtest",
    "tectonic":                "tectonic",
    "spacy":                   "spacy",
    "python-pptx":             "pptx",
    "joblib":                  "joblib",
    "protonvpn-cli":           "protonvpn_cli",
    "deep-translator":         "deep_translator",
    "accelerate":              "accelerate",
    "sentencepiece":           "sentencepiece",
    "tf-keras":                "tf_keras",
    "datasets":                "datasets",
    "sentence-transformers":   "sentence_transformers",
    "yt-dlp":                  "yt_dlp",
    "msal":                    "msal",
    "py7zr":                   "py7zr",
    "openai":                  "openai",
    "python-dotenv":           "dotenv",
    "seaborn":                 "seaborn",
    "pywin32":                 "win32com",
    "openpyxl":                "openpyxl",
    "pyperclip":               "pyperclip",
    "psutil":                  "psutil",
    "pandas":                  "pandas",
    "matplotlib":              "matplotlib",
    "xlrd":                    "xlrd",
    "python-docx":             "docx",
    "pyautogui":               "pyautogui",
    "keyboard":                "keyboard",
    "pynput":                  "pynput",
    "tensorflow":              "tensorflow",
    "keras":                   "keras",
    "opencv-python":           "cv2",
    "scikit-learn":            "sklearn",
    "numpy":                   "numpy",
    "pyttsx3":                 "pyttsx3",
    "beautifulsoup4":          "bs4",
    "lxml":                    "lxml",
    "selenium":                "selenium",
}

#function that install all packages 
def install_packages() -> None:
    """Instala apenas os pacotes que ainda não existem."""

    python = sys.executable

    for pip_name in LIBRARIES:

        try:
            importlib.metadata.version(pip_name)
            print(f"[OK] {pip_name}")

        except importlib.metadata.PackageNotFoundError:

            print(f"[INSTALL] {pip_name}")

            subprocess.check_call(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    "--user",
                    pip_name,
                ]
            )

#function that import all packages
def import_packages() -> dict[str, object]:
    """Importa todos os módulos e retorna um dicionário."""

    modules: dict[str, object] = {}

    for import_name in LIBRARIES.values():

        try:
            modules[import_name] = importlib.import_module(import_name)            
        except Exception as e02:
            print(f"Error: {e02}")            
            raise
    
    
    return modules
        
        

#example
if(False):

    install_packages()

    modules = import_packages()

    globals().update(modules)


#function that copy all files
def open_this_tree():
    try:
        pasta_script = Path(__file__).parent

        for origem in pasta_script.rglob("*.py"):

            # Não copia arquivos que já estão na pasta principal
            if origem.parent == pasta_script:
                continue

            destino = pasta_script / origem.name

            # Evita sobrescrever caso existam nomes iguais
            if destino.exists():
                i = 1
                while True:
                    novo_destino = pasta_script / f"{origem.stem}_{i}{origem.suffix}"
                    if not novo_destino.exists():
                        destino = novo_destino
                        break
                    i += 1

            shutil.copy2(origem, destino)

        return str(pasta_script)

    except Exception as e:
        print(e)
        return None

#function that clears all
def kill_pys():
    try:
        pasta_script = Path(__file__).parent
        meu_script = Path(__file__).resolve()

        for arquivo in pasta_script.glob("*.py"):

            # nunca apaga o próprio script
            if arquivo.resolve() == meu_script:
                continue

            arquivo.unlink()

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# function that clears all files of f".{ext}"
def kill_ext(ext):
    #ext = "py"
    try:
        pasta_script = Path(__file__).parent
        meu_script = Path(__file__).resolve()

        for arquivo in pasta_script.glob(("*."+f"{ext}")):

            # nunca apaga o próprio script
            if arquivo.resolve() == meu_script:
                continue

            arquivo.unlink()

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# function that clears all PNGs except logos
def kill_png():
    try:
        pasta_script = Path(__file__).parent

        for arquivo in pasta_script.glob("*.png"):

            # nunca apaga arquivos que contenham "logo" no nome
            if "logo" in arquivo.stem.lower():
                continue

            arquivo.unlink()

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# functions that clear all trashs
def kill_all00():
    if(clearpy):
        kill_pys()
    kill_ext("sta")
    kill_ext("out")
    kill_ext("inp")
    kill_ext("dat")
    kill_ext("cvg")
    kill_ext("12d")
    kill_ext("frd")
    kill_png()

# functions that clear all trashs
def kill_all():
    if(clear):
        kill_all00()

#main that could do all 
def main2try():
    open_this_tree()
    from testlock import is_it_locked
    from our_language import main_our_language
    from interface_v1dot0 import final_main_v1dot0 as interface
    is_it_locked()
    main_our_language()
    interface()
    kill_all()

#function tha try the main
def try_the_main(packs):
    try:
        main2try()
    except Exception as e00:
        kill_all()
        print(f"packages = {packs} \n\n Error: {e00} ")
        
#function tha try the main
def lets_do_it():
    try:
        import_packages()
        packages = True
        return f"{packages}"        
    except Exception as e01:
        print(f"Error: {e01}")
        try:
            install_packages()
        except Exception as e02:
            print(f"Error: {e02}")
        try:
            import_packages()
            packages = True
            return f"{packages}"
        except Exception as e03:
            packages = False
            print(f"Error: {e03}")
            packages = f"{packages}" + "\n" + f"{e01}" + "\n" + "{e02}" + "\n" + "{e03}"
            return f"{packages}"
        
#function that try the boh functions to  try
def try3main(txt,txt2):
    #try restore
    try:
        restore_original(txt)        
    except Exception as e08:
        print(f"Error: {e08}")
        #if there's no txt2 let's try to create it
        try:
            create_empty_txt(txt2)        
            restore_original(txt)
        except Exception as e07:
            print(f"Error: {e07}")
            #if there's no txt+txt2 let's try to create them
            try:
                create_empty_txt(txt)
                create_empty_txt(txt2)                
            except Exception as e07:
                print(f"Error: {e07}")                        
    ###main
    packs = lets_do_it()
    try_the_main(packs)

    #try clone
    try:
        clone_empty(txt)
    except Exception as eff:
        #if it doesn't work let's know the reason
        print(f"Error: {eff}")
        clone_empty(txt)
  
try3main("keys.txt","keys02.txt")