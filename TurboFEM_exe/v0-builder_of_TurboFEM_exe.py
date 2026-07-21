#  & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\TurboFEM_exe\builder_of_TurboFEM_exe.py #serie
# Start-Process "C:/Program Files/Python311/python.exe"  -ArgumentList "C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\TurboFEM_exe\builder_of_TurboFEM_exe.py" #parallelism

#this code is just to build the TurboFEM.exe
from pathlib import Path
import shutil
import subprocess
import sys
import time


tic = time.time()


def open_this_tree():

    try:

        # pasta onde está o script Python
        pasta_atual = Path(__file__).resolve().parent

        # procura todos os .py recursivamente
        for origem in pasta_atual.rglob("*.py"):

            # não copia arquivos que já estão na raiz
            if origem.parent == pasta_atual:
                continue


            destino = pasta_atual / origem.name


            # evita sobrescrever
            if destino.exists():

                i = 1

                while True:

                    novo_nome = (
                        f"{origem.stem}_{i}{origem.suffix}"
                    )

                    novo_destino = pasta_atual / novo_nome

                    if not novo_destino.exists():
                        destino = novo_destino
                        break

                    i += 1


            # copia mantendo data/permissões
            shutil.copy2(origem, destino)

            print(
                f"Copiado: {origem} -> {destino}"
            )


        return pasta_atual


    except Exception as e:

        print(e)
        return None



# vai para pasta correta
pasta_script = Path(__file__).resolve().parent

os_path = pasta_script.parent

# equivalente ao cd ..
import os
os.chdir(os_path)


# limpa build
build = Path("build")

if build.exists():
    shutil.rmtree(build)



python = sys.executable


try:

    # cria ícone
    subprocess.run(
        [
            python,
            "-c",
            (
                "from PIL import Image;"
                "Image.open('Fast-FEA-Logo.png').save("
                "'Fast-FEA-Logo.ico',"
                "sizes=[(16,16),(32,32),(48,48),(256,256)])"
            )
        ],
        check=True
    )


    # roda pyinstaller
    subprocess.run(
        [
            python,
            "-m",
            "PyInstaller",
            "TurboFEM.spec"
        ],
        check=True
    )


except Exception as e:

    print(e)



finally:

    # garante instalação
    subprocess.run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--user",
            "pyinstaller"
        ]
    )


    subprocess.run(
        [
            python,
            "-c",
            (
                "from PIL import Image;"
                "Image.open('Fast-FEA-Logo.png').save("
                "'Fast-FEA-Logo.ico',"
                "sizes=[(16,16),(32,32),(48,48),(256,256)])"
            )
        ]
    )


    subprocess.run(
        [
            python,
            "-m",
            "PyInstaller",
            "TurboFEM.spec"
        ]
    )


    print("end")



toc = time.time()

tempo = toc - tic

print(f"time[s]= {tempo}")