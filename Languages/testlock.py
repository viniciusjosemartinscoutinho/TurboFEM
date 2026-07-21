# & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V\testlock.py
import os
import subprocess
from pathlib import Path

def save_key(string: str, txt) -> None:
    Path(txt).write_text(string, encoding="utf-8")

def getkeys(string: str):
    # pasta onde está o script atual
    pasta_script = Path(__file__).parent

    # caminho do arquivo keys.txt
    arquivo = pasta_script / "keys.txt"

    # cria ou sobrescreve o arquivo com o conteúdo
    arquivo.write_text(string, encoding="utf-8")

def garantir_keys_txt(caminho):
    caminho = Path(caminho)

    # se for arquivo, pega a pasta
    pasta = caminho.parent if caminho.is_file() else caminho

    pasta.mkdir(parents=True, exist_ok=True)

    arquivo_keys = pasta / "keys.txt"

    arquivo_keys.touch(exist_ok=True)

    return arquivo_keys

def descobrir_melhor_pasta():
    # 1ª Opção: AppData Local (Melhor para desempenho)
    pasta_local = os.path.join(os.environ['LOCALAPPDATA'], "MeuCalculiX")
    
    # 2ª Opção: AppData Roaming (Excelente esconderijo e alta compatibilidade)
    pasta_roaming = os.path.join(os.environ['APPDATA'], "MeuCalculiX")
    
    # 3ª Opção: Zona Neutra Temporária (O plano de emergência)
    pasta_temp = "C:\\Temp\\MeuCalculiX"

    # Lista de tentativas na ordem de prioridade
    pastas_para_testar = [pasta_local, pasta_roaming, pasta_temp]

    for pasta in pastas_para_testar:
        try:
            os.makedirs(pasta, exist_ok=True)
            # Roda o teste real de execução (o comando cmd.exe)
            subprocess.run(
                ["cmd.exe", "/c", "echo ok"], 
                cwd=pasta, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            # Se o Windows não bloqueou o cmd.exe aqui, essa pasta é a vencedora!
            return pasta
        except Exception:
            # Se a TI bloqueou a execução aqui, pula para a próxima da lista
            continue
            
    return pasta_temp # Se tudo der errado, vai para a Temp

def is_it_locked():
    #lets test
    best_folder = descobrir_melhor_pasta()
    txttest = garantir_keys_txt(best_folder)
    getkeys(f"{txttest}")

#where is the cofig. data=
if(False):
    is_it_locked()


##end