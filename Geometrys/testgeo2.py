"""
geometria_barra_1d_param.py

Geometria de uma barra 1D dividida em N nos (N-1 elementos).
Sem material, sem carga, sem condicao de contorno -- so geometria.

No final, abre automaticamente o CGX (visualizador grafico que ja vem
junto com o CalculiX) e usa pyautogui para DIGITAR automaticamente os
comandos de visualizacao (plot n all, plus e all, etc.) dentro da
janela do CGX, contornando o bug do modo "-b"/.fbd que falha nesse
build do Windows com "Error in:sem_open".

Requisitos:
    pip install pyautogui

Uso:
    python geometria_barra_1d_param.py
"""

import math
import time
import shutil
import subprocess
from pathlib import Path

import psutil

try:
    import pyautogui
except Exception:
    # Cobre tanto ImportError (lib nao instalada) quanto qualquer outro
    # erro de inicializacao (ex: falta de display grafico), para que o
    # script nao quebre quando SHOW_MESH=False e o pyautogui nem seria
    # necessario.
    pyautogui = None


# =========================================================
# ---------- Funcoes auxiliares (sem efeito colateral) ----------
# =========================================================

def _ler_float(mensagem: str) -> float:
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(bruto)
            if valor <= 0:
                print("O valor deve ser positivo. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("Valor invalido. Digite um numero (ex: 25.0).")


def calcular_tempo_espera_continuo() -> float:
    """Calcula o tempo de espera de forma continua baseado na RAM e CPU."""
    mem = psutil.virtual_memory()
    ram_livre_gb = mem.available / (1024 * 1024 * 1024)
    cpu_uso = psutil.cpu_percent(interval=0.5)

    # Funcao continua
    tempo_espera = (cpu_uso / 100) * 5 + (1 / (ram_livre_gb + 1)) * 5

    # Limita o valor minimo e maximo
    tempo_espera = max(0.5, min(tempo_espera, 7.0))  # entre 0.5s e 7.0s

    return tempo_espera


def ai2() -> float:
    ai3 = calcular_tempo_espera_continuo()
    ai3 = ai3 * (2.0 ** (ai3 / 14.0))
    return ai3


def diagnosticar(rotulo: str, caminho: Path) -> None:
    abs_path = caminho.resolve()
    existe = abs_path.exists()
    print(f"[DIAGNOSTICO] {rotulo}")
    print(f"    caminho resolvido : {abs_path}")
    print(f"    existe no disco?  : {existe}")
    if existe:
        print(f"    eh arquivo?        : {abs_path.is_file()}")
        print(f"    tamanho (bytes)    : {abs_path.stat().st_size}")
    print()


def encontrar_cgx(cgx_path_override: str) -> str | None:
    if cgx_path_override and Path(cgx_path_override).is_file():
        return cgx_path_override

    no_path = shutil.which("cgx") or shutil.which("cgx.exe")
    if no_path:
        return no_path

    pasta_base = Path(r"C:\calculix")
    if pasta_base.is_dir():
        achados = list(pasta_base.rglob("cgx.exe"))
        if achados:
            return str(achados[0])

    return None


def gerar_geometria(base_dir: Path, l_comprimento: float, n_nodes: int):
    """Gera nos, elementos e escreve o arquivo .inp. Retorna (output_path, n_elements)."""
    n_elements = n_nodes - 1

    nodes = {}
    for i in range(n_nodes):
        nid = i + 1
        x = l_comprimento * i / (n_nodes - 1)
        nodes[nid] = (x, 0.0, 0.0)

    elements = {}
    for i in range(n_elements):
        eid = i + 1
        elements[eid] = (i + 1, i + 2)

    output_path = base_dir / "geometria_barra_1d_param.inp"

    print(f"[DIAGNOSTICO] BASE_DIR resolvido como: {base_dir}")
    print()

    lines = []
    lines.append("** Geometria: barra 1D parametrizada (N_NODES controla a malha)")
    lines.append("*HEADING")
    lines.append(f"Barra 1D - {n_nodes} nos, {n_elements} elementos")

    lines.append("*NODE")
    for nid, (x, y, z) in nodes.items():
        lines.append(f"{nid}, {x}, {y}, {z}")

    lines.append("*ELEMENT, TYPE=T3D2, ELSET=BARRA")
    for eid, (n1, n2) in elements.items():
        lines.append(f"{eid}, {n1}, {n2}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Arquivo gerado em: {output_path}")
    print(f"Total de nos: {n_nodes}")
    print(f"Total de elementos: {n_elements}")
    print()

    return output_path, n_elements


def abrir_cgx_e_digitar_comandos(cgx_exe: str, output_path: Path, base_dir: Path,
                                  espera_cgx_abrir: float, pausa_entre_comandos: float) -> None:
    diagnosticar("executavel cgx.exe encontrado", Path(cgx_exe))

    # Usamos "-c" (modo testado oficialmente, ja confirmado que funciona
    # no seu PC) para carregar a geometria. O "-b"/.fbd falha com
    # "Error in:sem_open" nesse build, entao em vez de depender do CGX
    # ler comandos de um arquivo, vamos SIMULAR a digitacao via teclado
    # com pyautogui, depois que a janela ja estiver aberta e carregada.
    print("Comando que sera executado:")
    print(f'    "{cgx_exe}" -c "{output_path.name}"')
    print(f"    (cwd = {base_dir})")
    print()

    try:
        subprocess.Popen(
            [cgx_exe, "-c", output_path.name],
            cwd=str(base_dir),
        )
        print("OK: CGX foi iniciado em modo -c (geometria carregada).")

        print(f"Aguardando {espera_cgx_abrir}s para a janela do CGX abrir...")
        time.sleep(espera_cgx_abrir)

        # Tenta encontrar e focar a janela do CGX pelo titulo, para
        # garantir que o teclado simulado chegue na janela certa e nao
        # no terminal/PowerShell.
        try:
            janelas = pyautogui.getWindowsWithTitle("CalculiX GraphiX")
            if janelas:
                janelas[0].activate()
                print("OK: janela 'CalculiX GraphiX' encontrada e focada.")
            else:
                print("AVISO: janela 'CalculiX GraphiX' nao foi encontrada pelo titulo.")
                print("Clique manualmente na janela do CGX AGORA, antes da digitacao comecar.")
        except Exception as e:
            print(f"AVISO: nao foi possivel focar a janela automaticamente ({e}).")
            print("Clique manualmente na janela do CGX AGORA, antes da digitacao comecar.")

        # Pequena pausa extra para garantir que o foco realmente mudou
        # antes de comecar a "digitar".
        time.sleep(ai2())

        comandos_cgx = [
            "plot n all",
            "plus e all",
            "plus n all",
            "frame",
        ]

        print()
        print("Iniciando digitacao automatica dos comandos no CGX...")
        for cmd in comandos_cgx:
            print(f"  -> digitando: {cmd}")
            try:
                pyautogui.typewrite(cmd, interval=0.02)
                pyautogui.press("enter")
            except Exception as e:
                # No Mac sem permissao de acessibilidade (ou Linux sem suporte
                # completo de automacao de teclado), pyautogui pode falhar aqui
                # mesmo tendo importado com sucesso antes. Isso nao deve travar
                # o script -- so avisa e segue para o proximo comando.
                print(f"     AVISO: nao foi possivel simular esse comando ({e}).")
                print(f"     Digite manualmente na janela do CGX: {cmd}")
            time.sleep(pausa_entre_comandos)

        print()
        print("OK: comandos enviados. A janela do CGX deve mostrar agora")
        print("a barra, os nos marcados, os numeros dos nos, e o zoom ajustado.")
        print()
        print("Se nada mudou na tela, o foco provavelmente nao estava na")
        print("janela do CGX no momento da digitacao. Tente clicar na janela")
        print("do CGX manualmente e rodar so os comandos acima por digitacao normal,")
        print("ou aumente ESPERA_CGX_ABRIR no topo do script e tente de novo.")

    except Exception as e:
        print(f"ERRO durante o processo de automacao: {e}")


# =========================================================
# ---------- main() ----------
# =========================================================

L2 = False
N2 = False
def main_geo(L2=150,N2=15) -> None:
    # ---------- Parametros que voce escolhe ----------
    L = 150
    if((L2-150)==0):
        L = L
    else:
        L = L2
    # L = _ler_float("Comprimento axial L [mm]: ")

    SHOW_MESH = False  # True/False -- abre o CGX automaticamente apos gerar o .inp

    n_nodes_raw = 15
    if((N2-15)==0):
        n_nodes_raw = n_nodes_raw
    else:
        n_nodes_raw = N2
    
    # N_NODES = _ler_float("N Elementos: ")
    N_NODES = int(math.ceil(float(1 + n_nodes_raw)))

    CGX_PATH_OVERRIDE = r""  # ex: r"C:\calculix\CalculiX-2.23.0-win-x64\bin\cgx.exe"

    # Tempo de espera (segundos) para a janela do CGX abrir e terminar de
    # carregar o .inp antes de comecarmos a "digitar" os comandos.
    espera_cgx_abrir = ai2()

    # Pausa (segundos) entre cada comando digitado.
    pausa_entre_comandos = 1.0 * ai2()

    # ---------- Geracao automatica da geometria ----------
    base_dir = Path(__file__).resolve().parent
    output_path, n_elements = gerar_geometria(base_dir, L, N_NODES)

    # ---------- Abertura opcional do CGX ----------
    print("Procurando o executavel do CGX para abrir a visualizacao...")

    if not SHOW_MESH:
        print("SHOW_MESH = False -> pulando abertura do CGX. So o .inp foi gerado.")
        return

    cgx_exe = encontrar_cgx(CGX_PATH_OVERRIDE)

    if cgx_exe is None:
        print("AVISO: cgx.exe nao foi encontrado automaticamente.")
        print("Preencha a variavel CGX_PATH_OVERRIDE no topo do script com o")
        print("caminho completo do cgx.exe, ou rode manualmente:")
        print(f'  cgx -c "{output_path.name}"')
        return

    if pyautogui is None:
        print("AVISO: a biblioteca 'pyautogui' nao esta instalada.")
        print("Instale com:  pip install pyautogui")
        print("Depois rode este script novamente.")
        return

    abrir_cgx_e_digitar_comandos(
        cgx_exe, output_path, base_dir, espera_cgx_abrir, pausa_entre_comandos
    )


if(False):
    main_geo()