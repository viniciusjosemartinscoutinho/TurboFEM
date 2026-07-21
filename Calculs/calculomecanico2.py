#SHOW_MESH_CGX = True
SHOW_MESH_CGX = False




"""
calculomecanico.py

Script principal de calculo mecanico para barra/viga 1D no CalculiX.

Fluxo:
    1) Varredura RECURSIVA a partir da pasta PAI da pasta do script,
       procurando o .inp mais recente (mesmo mecanismo do
       editar_inp_material_secao.py).
    2) Garante que os elementos sejam do tipo B31 (viga 3D), trocando
       automaticamente se o .inp ainda estiver com T3D2 (treliça) --
       B31 e o unico tipo que suporta flexao, torcao e carga distribuida.
    3) Pergunta ao usuario se quer impor DESLOCAMENTO ou ESFORCOS
       (modulo carregamento.py), sempre engastando o no inicial (x=0).
    4) Escreve o STEP completo no .inp (boundary + load + STATIC +
       NODE FILE U + EL FILE S).
    5) Executa o CalculiX (ccx) sobre esse .inp.
    6) Le o .frd resultante (modulo frd_parser.py) e calcula os campos
       derivados (von Mises, Tresca, principais, etc.).
    7) Pergunta ao usuario quais graficos quer ver (um campo especifico,
       ou "all" para gerar todos), e gera:
         - 1 grafico da geometria deformada (deslocamentos amplificados)
         - 1 grafico por campo escolhido, geometria reta colorida
           azul->vermelho conforme o valor do campo.

Uso:
    python calculomecanico.py
"""

import subprocess
import shutil
import time
from pathlib import Path

#dircode
the_script_dir = Path(__file__).resolve().parent


try:
    import pyautogui
except Exception:
    # Cobre ImportError (lib nao instalada) e qualquer erro de
    # inicializacao (ex: falta de display grafico), para que o script
    # nao quebre quando SHOW_MESH_CGX=False e o pyautogui nem seria
    # necessario.
    pyautogui = None

from carregamento_copy_copy import definir_carregamento
from frd_parser import (
    parse_frd, calcular_von_mises, calcular_tresca, calcular_tensoes_principais,
    calcular_deformacoes_principais,
)
from plotagem import (
    plotar_geometria_deformada, plotar_geometria_colorida_por_campo,
    escolher_fator_escala_automatico, CAMPOS_DISPONIVEIS,
)


CGX_PATH_OVERRIDE = r""  # ex: r"C:\calculix\CalculiX-2.23.0-win-x64\bin\cgx.exe"
CCX_PATH_OVERRIDE = r""  # ex: r"C:\calculix\CalculiX-2.23.0-win-x64\bin\ccx.exe"

# Se True, alem dos PNGs gerados pelo matplotlib (que sempre funcionam
# em qualquer PC), o script tambem tenta abrir o resultado direto no
# CGX (visualizador nativo do CalculiX), mostrando a geometria
# deformada colorida por tensao -- igual o GIBIANE faz no Cast3M.
# Requer 'pip install pyautogui' e so foi validado no Windows; em
# outros SOs ou se a automacao falhar, o script avisa e segue normal,
# sem quebrar (os PNGs continuam sendo gerados independente disso).

ESPERA_CGX_ABRIR = 3.0
PAUSA_ENTRE_COMANDOS = 1.0
PAUSA_APOS_DS = 3.0  # pausa extra apos "ds", onde os testes mostraram falha de timing

def encontrar_executavel_local(nome_executavel: str) -> str | None:
    """
    Procura recursivamente um executavel a partir da pasta do script.
    Funciona para ccx.exe e cgx.exe.
    """

    for caminho in the_script_dir.rglob(nome_executavel):

        if caminho.is_file():
            print(f"OK: {nome_executavel} encontrado:")
            print(f"    {caminho}")
            return str(caminho)

    return None

def diagnosticar(rotulo: str, caminho: Path) -> None:
    abs_path = caminho.resolve()
    existe = abs_path.exists()
    print(f"[DIAGNOSTICO] {rotulo}")
    print(f"    caminho resolvido : {abs_path}")
    print(f"    existe no disco?  : {existe}")
    if existe:
        print(f"    tamanho (bytes)    : {abs_path.stat().st_size}")
    print()


def encontrar_inp_mais_recente(pasta_raiz: Path) -> Path | None:
    candidatos = list(pasta_raiz.rglob("*.inp"))
    if not candidatos:
        return None
    return max(candidatos, key=lambda p: p.stat().st_mtime)


def encontrar_executavel(nome: str, override: str, pasta_base_windows: str) -> str | None:
    if override and Path(override).is_file():
        return override

    no_path = shutil.which(nome) or shutil.which(nome + ".exe")
    if no_path:
        return no_path

    pasta_base = Path(pasta_base_windows)
    if pasta_base.is_dir():
        achados = list(pasta_base.rglob(f"{nome}.exe"))
        if achados:
            return str(achados[0])

    return None


def converter_beam_general_section_para_rect(linhas: list[str]) -> list[str]:
    """
    O CalculiX real rejeita *BEAM GENERAL SECTION para elementos B31
    (esse cartao so e valido para o elemento de usuario U1 -- confirmado
    rodando o solver real e recebendo o erro "is not a U1 element").

    Para elementos B31 padrao, a secao precisa ser definida por forma
    geometrica (*BEAM SECTION, SECTION=RECT/CIRC/PIPE/BOX), nao por
    area/inercia diretos.

    Como ja temos A e Iy calculados (vindos do editar_inp_material_secao.py),
    convertemos para uma secao RECTANGULAR EQUIVALENTE que reproduz
    exatamente a mesma area e o mesmo momento de inercia principal Iy:

        h = sqrt(12 * Iy / A)
        b = A / h

    Isso preserva A e Iy exatamente. Iz pode diferir do valor original
    se a secao real nao fosse retangular (ex: circular, perfil I) --
    para fins de flexao no plano principal (Iy) e area axial, o
    resultado e equivalente; para Iz e torcao (J) pode haver pequena
    diferenca, que e aceitavel para fins de portfolio/estudo.
    """
    linhas_corrigidas = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        linha_upper = linha.strip().upper()

        if linha_upper.startswith("*BEAM GENERAL SECTION"):
            # Le os parametros do cartao (ELSET, MATERIAL)
            elset = ""
            material = ""
            for parte in linha_upper.split(","):
                parte = parte.strip()
                if parte.startswith("ELSET="):
                    elset = parte.split("=")[1]
                if parte.startswith("MATERIAL="):
                    material = parte.split("=")[1]

            # Linha seguinte: "A, 0.0, Iy, Iz"
            dados_linha = linhas[i + 1].strip().rstrip(",")
            valores = [float(v) for v in dados_linha.split(",")]
            A, _, Iy, Iz = valores[0], valores[1], valores[2], valores[3]

            # Linha seguinte: vetor de orientacao (mantemos igual)
            linha_vetor = linhas[i + 2]

            h = (12.0 * Iy / A) ** 0.5 if A > 0 and Iy > 0 else 1.0
            b = A / h if h > 0 else 1.0

            linhas_corrigidas.append(
                f"*BEAM SECTION, ELSET={elset}, MATERIAL={material}, SECTION=RECT"
            )
            linhas_corrigidas.append(f"{h}, {b}")
            linhas_corrigidas.append(linha_vetor)

            i += 3
            continue

        linhas_corrigidas.append(linha)
        i += 1

    return linhas_corrigidas


def garantir_elemento_b31(linhas: list[str]) -> tuple[list[str], str]:
    """
    Verifica se o .inp usa T3D2 (trelica) e, se sim, troca para B31
    (viga), que e o unico tipo que suporta flexao/torcao/carga
    distribuida. Retorna (linhas_corrigidas, nome_do_elset_da_barra).
    """
    elset_barra = "BARRA"
    linhas_corrigidas = []
    trocou = False

    for linha in linhas:
        linha_upper = linha.strip().upper()
        if linha_upper.startswith("*ELEMENT") and "T3D2" in linha_upper:
            nova_linha = linha.upper().replace("T3D2", "B31")
            linhas_corrigidas.append(nova_linha)
            trocou = True
            if "ELSET=" in linha_upper:
                elset_barra = linha_upper.split("ELSET=")[1].split(",")[0].strip()
        else:
            linhas_corrigidas.append(linha)

    if trocou:
        print("AVISO: elementos T3D2 (trelica) encontrados e convertidos para B31 (viga),")
        print("       necessario para suportar flexao, torcao e carga distribuida.")
        print()

    return linhas_corrigidas, elset_barra


def extrair_todos_os_nos(linhas: list[str]) -> dict:
    """
    Le o bloco *NODE do .inp e retorna TODAS as coordenadas, no formato
    {node_id: (x, y, z)}. Usado para mapear a linha neutra da viga
    apos a expansao de secao feita pelo CalculiX no .frd.
    """
    nodes = {}
    dentro_de_node = False

    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.upper().startswith("*NODE"):
            dentro_de_node = True
            continue
        if dentro_de_node:
            if linha_strip.startswith("*"):
                break
            partes = [p.strip() for p in linha_strip.split(",")]
            if len(partes) >= 4:
                try:
                    nid = int(partes[0])
                    x, y, z = float(partes[1]), float(partes[2]), float(partes[3])
                    nodes[nid] = (x, y, z)
                except ValueError:
                    continue

    return nodes


def extrair_nos_extremos(linhas: list[str]) -> tuple[int, int]:
    """
    Le o bloco *NODE do .inp e retorna (node_id_minimo_x, node_id_maximo_x).
    """
    nodes = {}
    dentro_de_node = False

    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.upper().startswith("*NODE"):
            dentro_de_node = True
            continue
        if dentro_de_node:
            if linha_strip.startswith("*"):
                break
            partes = [p.strip() for p in linha_strip.split(",")]
            if len(partes) >= 2:
                try:
                    nid = int(partes[0])
                    x = float(partes[1])
                    nodes[nid] = x
                except ValueError:
                    continue

    if not nodes:
        raise ValueError("Nenhum no encontrado no bloco *NODE do .inp.")

    node_inicio = min(nodes, key=lambda n: nodes[n])
    node_final = max(nodes, key=lambda n: nodes[n])
    return node_inicio, node_final


def remover_step_antigo(linhas: list[str]) -> list[str]:
    """
    Remove qualquer *STEP ... *END STEP previamente inserido por uma
    execucao anterior deste script.
    """
    resultado = []
    dentro_de_step = False
    for linha in linhas:
        linha_upper = linha.strip().upper()
        if linha_upper.startswith("*STEP"):
            dentro_de_step = True
            continue
        if linha_upper.startswith("*END STEP"):
            dentro_de_step = False
            continue
        if not dentro_de_step:
            resultado.append(linha)
    return resultado


def montar_step(linhas_carregamento: list[str]) -> list[str]:
    return (
        ["*STEP", "*STATIC"]
        + linhas_carregamento
        + ["*NODE FILE", "U", "*EL FILE, OUTPUT=3D", "S, E", "*END STEP"]
    )

def mapear_nos_linha_neutra(nodes_inp: dict, nodes_frd: dict) -> dict:

    mapa = {}

    for node_id_orig, (x_orig, y_orig, z_orig) in nodes_inp.items():

        melhor_id = None
        melhor_distancia = float("inf")

        for node_id_frd, (x_frd, y_frd, z_frd) in nodes_frd.items():

            if abs(x_frd - x_orig) > 1e-2:
                continue

            distancia = y_frd**2 + z_frd**2

            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_id = node_id_frd

        if melhor_id is not None:
            mapa[node_id_orig] = melhor_id

    return mapa

def mapear_nos_linha_neutra_v0(nodes_inp: dict, nodes_frd: dict) -> dict:
    """
    O CalculiX expande elementos B31 em multiplos nos de secao no .frd
    (confirmado experimentalmente: um elemento B31 com 2 nos gera ~8
    nos de secao no resultado, sem preservar os IDs originais do .inp).

    Para conseguirmos plotar a LINHA NEUTRA da viga (o eixo, nao a
    superficie da secao), mapeamos cada no original do .inp para o(s)
    no(s) do .frd que estao na mesma posicao X e o mais proximo de
    Y=0, Z=0 (centro da secao).

    Retorna um dicionario {node_id_original_do_inp: node_id_no_frd}.
    """
    mapa = {}
    for node_id_orig, (x_orig, y_orig, z_orig) in nodes_inp.items():
        melhor_id = None
        melhor_distancia = float("inf")
        for node_id_frd, (x_frd, y_frd, z_frd) in nodes_frd.items():
            if abs(x_frd - x_orig) > 1e-6:
                continue
            distancia = (y_frd - y_orig) ** 2 + (z_frd - z_orig) ** 2
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_id = node_id_frd
        if melhor_id is not None:
            mapa[node_id_orig] = melhor_id
    return mapa


def filtrar_dados_pela_linha_neutra(dados: dict, nodes_inp: dict) -> dict:
    """
    Filtra nodes/disp/stress do resultado do .frd para conter apenas
    os nos correspondentes a linha neutra original da viga (definida
    pelo .inp), evitando que a geometria de secao expandida (B31 ->
    multiplos nos por secao) "polua" os graficos com pontos extras.
    """
    mapa = mapear_nos_linha_neutra(nodes_inp, dados["nodes"])

    nodes_filtrados = {}
    disp_filtrados = {}
    stress_filtrados = {}
    strain_filtrados = {}

    for node_id_orig, node_id_frd in mapa.items():
        # Usa a posicao ORIGINAL do .inp (linha neutra real, x,0,0),
        # nao a posicao do no-frd selecionado, que e um no de CANTO da
        # secao expandida pelo CalculiX (ex: y=-25, nao y=0).
        nodes_filtrados[node_id_orig] = nodes_inp[node_id_orig]
        if node_id_frd in dados["disp"]:
            disp_filtrados[node_id_orig] = dados["disp"][node_id_frd]
        if node_id_frd in dados["stress"]:
            stress_filtrados[node_id_orig] = dados["stress"][node_id_frd]
        if node_id_frd in dados.get("strain", {}):
            strain_filtrados[node_id_orig] = dados["strain"][node_id_frd]

    return {
        "nodes": nodes_filtrados,
        "disp": disp_filtrados,
        "stress": stress_filtrados,
        "strain": strain_filtrados,
    }

def encontrar_cgx() -> str | None:
    return encontrar_executavel_local("cgx.exe") #encontrar_executavel("cgx", CGX_PATH_OVERRIDE, r"C:\calculix")



# Mapeia nosso nome interno de campo para a entidade NATIVA do CGX,
# confirmada na documentacao oficial (cgx pre-defined calculations):
#   von Mises  -> entidade "Mises"
#   principais -> entidades "P1", "P2", "P3" (worstPS = maior valor absoluto)
# Tresca e sigma_axial puro nao tem entidade pre-calculada equivalente
# direta no cgx (Tresca exigiria escrever uma "user entity"), entao
# para esses usamos a aproximacao mais proxima disponivel nativamente.
_ENTIDADE_CGX_POR_CAMPO = {
    "von_mises": (2, "Mises"),
    "sigma_max": (2, "P1"),
    "sigma_min": (2, "P3"),
    "tresca": (2, "worstPS"),   # aproximacao: maior valor principal absoluto
    "sigma_axial": (2, "SXX"),
    "epsilon_max": (3, "P1"),
    "epsilon_min": (3, "P3"),
}


def perguntar_fator_amplificacao(fator_automatico: float) -> float:
    """
    Pergunta ao usuario o fator de amplificacao (anamorfismo) usado
    para exibir a geometria deformada -- igual ao Cast3M/GIBIANE pede
    um fator de deformee antes de desenhar.
    """
    print()
    print(f"Fator de amplificacao calculado automaticamente: {fator_automatico:.4f}")
    resposta = ""#in-put("Pressione ENTER para usar esse valor, ou digite outro fator manualmente: ").strip().replace(",", ".")
    if not resposta:
        return fator_automatico
    try:
        return float(resposta)
    except ValueError:
        print("Valor invalido, usando o fator automatico.")
        return fator_automatico


def _abrir_uma_janela_cgx(cgx_exe: str, frd_path: Path, titulo_log: str,
                            comandos: list[str], n_janelas_esperadas: int = 1) -> None:
    """
    Abre UMA instancia do CGX no .frd e digita os comandos dados em
    sequencia. Cada chamada desta funcao abre uma janela NOVA e
    independente (subprocess.Popen separado) -- assim a janela de
    deslocamento e a janela de tensao ficam abertas ao mesmo tempo,
    cada uma travada no seu proprio campo, igual o GIBIANE no Cast3M
    mostra paineis separados para deformada e tensao.

    IMPORTANTE: testes anteriores mostraram "ERROR in formulation" em
    QUALQUER comando "comp" (mesmo "comp D1", uma componente basica que
    sempre deveria funcionar) quando executado logo apos um "ds". Isso
    indica que o erro NAO e sobre qual entidade foi pedida, e sim um
    problema de TIMING: o CGX ainda esta processando o carregamento do
    dataset internamente quando o "comp" chega. Por isso aplicamos uma
    pausa extra, maior que a pausa padrao entre os demais comandos,
    especificamente apos qualquer comando que comece com "ds".

    n_janelas_esperadas: usado por timepontosleepinteligenteX para
    saber quantas janelas "CalculiX GraphiX" devem existir no total
    apos esta chamada -- a primeira janela usa 1, a segunda (que abre
    enquanto a primeira ainda esta na tela) usa 2, e assim por diante.
    """
    print()
    print(f"--- Abrindo janela do CGX: {titulo_log} ---")
    print(f'    "{cgx_exe}" "{frd_path.name}"   (cwd = {frd_path.parent})')

    try:
        subprocess.Popen([cgx_exe, frd_path.name], cwd=str(frd_path.parent))
    except Exception as e:
        print(f"AVISO: nao foi possivel abrir o CGX para '{titulo_log}' ({e}).")
        return

    timepontosleepinteligenteX(
        titulo_janela="CalculiX GraphiX",
        n_janelas_esperadas=n_janelas_esperadas,
        passo_segundos=3.0,
        timeout_segundos=60.0,
    )
    #time.sleep(3)

    if pyautogui is None:
        print("AVISO: pyautogui nao disponivel -- digite os comandos manualmente:")
        for cmd in comandos:
            print(f"    {cmd}")
        return

    try:
        janelas = pyautogui.getWindowsWithTitle("CalculiX GraphiX")
        if janelas:
            # A janela mais recente (a que acabamos de abrir) costuma
            # ser a ultima da lista retornada pelo pyautogui.
            janelas[-1].activate()
        else:
            print("AVISO: janela do CGX nao encontrada pelo titulo -- clique nela agora.")
    except Exception as e:
        print(f"AVISO: nao foi possivel focar a janela automaticamente ({e}).")
        print("Clique na janela do CGX agora, antes da digitacao comecar.")

    #time.sleep(1.0)

    for cmd in comandos:
        print(f"  -> digitando: {cmd}")
        try:
            pyautogui.typewrite(cmd, interval=0.02)
            pyautogui.press("enter")
        except Exception as e:
            print(f"     AVISO: nao foi possivel simular esse comando ({e}).")
            print(f"     Digite manualmente na janela do CGX: {cmd}")

        if cmd.strip().lower().startswith("ds"):
            # Pausa extra apos "ds" -- e exatamente o ponto onde os
            # testes anteriores mostraram falha de timing.
            print(f"     (pausa extra de {PAUSA_APOS_DS:.1f}s para o CGX processar o dataset...)")
            time.sleep(PAUSA_APOS_DS)
        else:
            time.sleep(PAUSA_ENTRE_COMANDOS)



def abrir_cgx_pos_processamento(frd_path: Path, campos: list[str], fator_escala: float) -> None:
    """
    Abre VARIAS janelas separadas do CGX, direto no .frd (sem -c, sem -b):

        Janela 1            : geometria deformada (deslocamento), com
                               o fator de amplificacao escolhido pelo
                               usuario. Aberta UMA UNICA VEZ, comum a
                               todos os campos.
        Janela 2, 3, 4, ...  : uma janela POR campo em "campos", cada
                               uma mostrando a geometria SEM deformar,
                               colorida pela tensao/deformacao daquele
                               campo especifico.

    Em cada janela de tensao, a ORDEM dos comandos e: primeiro
    "comp <entidade>" e SO DEPOIS "scal d <fator>" (quando aplicavel) --
    ordem escolhida apos observar que "scal d" antes de "comp" fazia o
    CGX reverter para o dataset de deslocamento.

    Cada janela de campo tem seu PROPRIO try/except: se abrir ou
    digitar comandos para um campo falhar (ex: a entidade nao for
    calculavel nesse .frd), isso e reportado mas NAO impede as demais
    janelas de serem abertas -- evita que um campo problematico
    interrompa a visualizacao de todos os outros quando o usuario
    escolheu "all".

    Se pyautogui nao estiver disponivel ou a automacao falhar, avisa e
    nao interrompe o restante do script (os PNGs ja gerados continuam
    validos independente disso).
    """
    if not SHOW_MESH_CGX:
        return

    if pyautogui is None:
        print("AVISO: pyautogui nao disponivel -- pulando abertura do CGX.")
        print("Instale com 'pip install pyautogui' para habilitar essa visualizacao.")
        return

    cgx_exe = encontrar_cgx()
    if cgx_exe is None:
        print("AVISO: cgx.exe nao encontrado -- pulando abertura do CGX.")
        return

    fator_usuario = perguntar_fator_amplificacao(fator_escala)

    # ---- Janela 1: deslocamento (geometria deformada) -----------------
    # Aberta uma unica vez, antes do loop de campos.
    try:
        comandos_deslocamento = [
            "ds 1 e",
            "comp D1",
            f"scal d {fator_usuario:.4f}",
            "frame",
        ]
        #time.sleep(3)
        _abrir_uma_janela_cgx(
            cgx_exe, frd_path,
            "Janela de deslocamento (geometria deformada)",
            comandos_deslocamento,
            n_janelas_esperadas=1,
        )
        (3)
    except Exception as e:
        print(f"AVISO: falha ao abrir a janela de deslocamento ({e}). Seguindo mesmo assim.")

    # ---- Uma janela de tensao/deformacao POR campo escolhido ----------
    janelas_abertas_ate_agora = 1
    for campo in campos:
        numero_dataset, entidade = _ENTIDADE_CGX_POR_CAMPO.get(campo, (2, "Mises"))
        janelas_abertas_ate_agora += 1

        try:
            comandos_tensao = [
                f"ds {numero_dataset} e",
                f"comp {entidade}",
                "frame",
            ]
            _abrir_uma_janela_cgx(
                cgx_exe, frd_path,
                f"Janela - {campo} (geometria original colorida)",
                comandos_tensao,
                n_janelas_esperadas=janelas_abertas_ate_agora,
            )
            print(f"OK: janela do campo '{campo}' (entidade '{entidade}') solicitada.")
        except Exception as e:
            print(f"AVISO: falha ao abrir a janela do campo '{campo}' ({e}).")
            print(f"       Pulando para o proximo campo, se houver.")

    print()
    print("=== CGX: janelas solicitadas ===")
    print("A primeira janela deveria mostrar a barra deformada (deslocamento amplificado).")
    print("Cada janela seguinte deveria mostrar a barra reta colorida pelo campo correspondente.")
    print("Se alguma janela nao colorir e mostrar 'ERROR in formulation', essa")
    print("entidade pode nao ser calculavel para este .frd -- me envie a mensagem")
    print("exata e qual campo, para eu investigar uma entidade alternativa.")


def timepontosleepinteligenteX(titulo_janela: str = "CalculiX GraphiX",
                                  n_janelas_esperadas: int = 1,
                                  passo_segundos: float = 3.0,
                                  timeout_segundos: float = 6000000.0) -> bool:
    """
    Espera de forma inteligente a janela do CGX abrir, em vez de usar
    um time.sleep fixo (que pode ser curto demais em PC lento, ou
    desperdicar tempo em PC rapido).

    Funciona em loop: a cada passo_segundos, verifica via
    pyautogui.getWindowsWithTitle(titulo_janela) se o NUMERO de
    janelas com esse titulo ja chegou a n_janelas_esperadas. Se sim,
    da break e retorna True. Se passar do timeout_segundos sem achar,
    desiste e retorna False (mas nao trava o script -- quem chamar
    decide o que fazer, ex: seguir mesmo assim com um sleep de
    seguranca).

    Parametros:
        titulo_janela       : titulo exato da janela a procurar.
        n_janelas_esperadas  : quantas janelas com esse titulo devem
                               existir para considerar "aberta" (use 2
                               se voce ja abriu uma janela antes e esta
                               esperando a SEGUNDA aparecer).
        passo_segundos       : intervalo entre cada verificacao.
        timeout_segundos     : tempo maximo total de espera antes de
                               desistir (protecao contra loop infinito
                               de verdade).

    Retorna:
        True  se a janela foi detectada dentro do timeout.
        False se o timeout foi atingido sem detectar a janela (ou se
              pyautogui nao estiver disponivel para verificar).
    """
    if pyautogui is None:
        print("AVISO: pyautogui indisponivel -- nao e possivel detectar a janela.")
        print(f"Usando pausa fixa de seguranca de {passo_segundos:.1f}s.")
        time.sleep(passo_segundos)
        return False

    tempo_decorrido = 0.0
    while tempo_decorrido < timeout_segundos:
        try:
            janelas = pyautogui.getWindowsWithTitle(titulo_janela)
            n_janelas = len(janelas)
        except Exception as e:
            print(f"AVISO: erro ao verificar janelas ({e}). Usando pausa fixa.")
            time.sleep(passo_segundos)
            return False

        if n_janelas >= n_janelas_esperadas:
            print(f"OK: janela '{titulo_janela}' detectada apos {tempo_decorrido:.1f}s "
                  f"({n_janelas} janela(s) encontrada(s)).")
            return True

        print(f"  ...aguardando janela '{titulo_janela}' abrir "
              f"({n_janelas}/{n_janelas_esperadas} encontrada(s), "
              f"{tempo_decorrido:.1f}s decorridos)...")
        time.sleep(passo_segundos)
        tempo_decorrido += passo_segundos

    print(f"AVISO: timeout de {timeout_segundos:.1f}s atingido sem detectar a janela.")
    print("Seguindo mesmo assim -- clique na janela do CGX manualmente se necessario.")
    return False


def main_ccx(option21,qy_XOR_ux, fy_XOR_uy, fx_XOR_uz, mz, tx):
    script_dir = Path(__file__).resolve().parent
    pasta_pai = script_dir.parent

    print(f"[DIAGNOSTICO] Pasta do script: {script_dir}")
    print(f"[DIAGNOSTICO] Pasta pai (raiz da varredura): {pasta_pai}")
    print()

    inp_path = encontrar_inp_mais_recente(pasta_pai)
    if inp_path is None:
        print(f"ERRO: nenhum .inp encontrado a partir de {pasta_pai}")
        return

    print(f"OK: .inp mais recente selecionado -> {inp_path}")
    diagnosticar(".inp selecionado", inp_path)

    conteudo = inp_path.read_text(encoding="utf-8")
    linhas = conteudo.splitlines()

    linhas, elset_barra = garantir_elemento_b31(linhas)
    linhas = converter_beam_general_section_para_rect(linhas)
    linhas = remover_step_antigo(linhas)

    try:
        node_inicio, node_final = extrair_nos_extremos(linhas)
    except ValueError as e:
        print(f"ERRO: {e}")
        return

    nodes_inp_originais = extrair_todos_os_nos(linhas)

    print(f"No inicial (engaste, x=0): {node_inicio}")
    print(f"No final (x=L): {node_final}")

    linhas_carregamento, resumo_carregamento = definir_carregamento(
        node_inicio, node_final, elset_barra,option21,qy_XOR_ux, fy_XOR_uy, fx_XOR_uz, mz, tx
    )

    linhas_step = montar_step(linhas_carregamento)
    linhas_finais = linhas + linhas_step

    print()
    print("=== Resumo do carregamento ===")
    print(resumo_carregamento)
    print()

    confirmacao = "s" #in-put(f"Confirmar edicao de '{inp_path.name}' e execucao no CalculiX? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operacao cancelada pelo usuario. Nenhum arquivo foi alterado.")
        return

    inp_path.write_text("\n".join(linhas_finais) + "\n", encoding="utf-8")
    print(f"OK: .inp atualizado -> {inp_path}")
    print()

    #change here
    #ccx_exe = encontrar_executavel("ccx", CCX_PATH_OVERRIDE, r"C:\calculix")
    ccx_exe = encontrar_executavel_local("ccx.exe")
    if ccx_exe is None:
        print("AVISO: ccx.exe nao encontrado automaticamente.")
        print("Preencha CCX_PATH_OVERRIDE no topo do script, ou rode manualmente:")
        print(f'  ccx "{inp_path.stem}"')
        return

    print(f"OK: ccx encontrado em {ccx_exe}")
    jobname = inp_path.stem
    print(f"Executando: ccx {jobname}  (cwd = {inp_path.parent})")
    print()

    resultado = subprocess.run(
        [ccx_exe, jobname],
        cwd=str(inp_path.parent),
        capture_output=True,
        text=True,
    )
    print(resultado.stdout[-3000:])
    if resultado.returncode != 0:
        print("ERRO: ccx terminou com erro. Saida de erro:")
        print(resultado.stderr[-2000:])
        return

    frd_path = inp_path.parent / f"{jobname}.frd"
    if not frd_path.exists():
        print(f"ERRO: arquivo de resultado {frd_path} nao foi gerado.")
        return

    print(f"OK: resultado gerado -> {frd_path}")
    dados_brutos = parse_frd(frd_path)

    if not dados_brutos["disp"] or not dados_brutos["stress"]:
        print("AVISO: o .frd nao contem DISP e/ou STRESS. Verifique se o solver")
        print("convergiu (cheque o arquivo .dat / saida do ccx acima).")
        return

    print(f"[DIAGNOSTICO] Nos no .frd (incluindo expansao de secao do B31): {len(dados_brutos['nodes'])}")
    dados = filtrar_dados_pela_linha_neutra(dados_brutos, nodes_inp_originais)
    print(f"[DIAGNOSTICO] Nos filtrados na linha neutra (eixo da viga): {len(dados['nodes'])}")
    print()

    campos_calculados = {
        "von_mises": {},
        "tresca": {},
        "sigma_axial": {},
        "sigma_max": {},
        "sigma_min": {},
    }
    for node_id, s in dados["stress"].items():
        campos_calculados["von_mises"][node_id] = calcular_von_mises(s)
        campos_calculados["tresca"][node_id] = calcular_tresca(s)
        campos_calculados["sigma_axial"][node_id] = s[0]
        smin, _, smax = calcular_tensoes_principais(s)
        campos_calculados["sigma_max"][node_id] = smax
        campos_calculados["sigma_min"][node_id] = smin

    if dados.get("strain"):
        campos_calculados["epsilon_max"] = {}
        campos_calculados["epsilon_min"] = {}
        for node_id, e in dados["strain"].items():
            emin, _, emax = calcular_deformacoes_principais(e)
            campos_calculados["epsilon_max"][node_id] = emax
            campos_calculados["epsilon_min"][node_id] = emin

    print()
    print("=== Escolha dos graficos ===")
    print("Campos disponiveis:")
    opcoes_lista = list(CAMPOS_DISPONIVEIS.keys())
    for i, chave in enumerate(opcoes_lista, start=1):
        disponivel = "" if chave in campos_calculados else "  (nao disponivel)"
        print(f"{i} - {CAMPOS_DISPONIVEIS[chave]}{disponivel}")
    print(f"{len(opcoes_lista)+1} - all (plotar todos os campos disponiveis)")
    print()

    escolha = "all"#in-put("Escolha o numero do campo (ou 'all'): ").strip().lower()

    if escolha == "all" or escolha == str(len(opcoes_lista) + 1):
        campos_escolhidos = [c for c in opcoes_lista if c in campos_calculados]
    else:
        try:
            indice = int(escolha) - 1
            campos_escolhidos = [opcoes_lista[indice]]
        except (ValueError, IndexError):
            print("Opcao invalida. Usando 'von_mises' como padrao.")
            campos_escolhidos = ["von_mises"]

    fator = escolher_fator_escala_automatico(dados["nodes"], dados["disp"])
    caminho_deformada = inp_path.parent / f"{jobname}_deformada.png"
    plotar_geometria_deformada(dados["nodes"], dados["disp"], fator, caminho_deformada)
    print(f"OK: grafico de deformacao gerado -> {caminho_deformada}")

    for campo in campos_escolhidos:
        if campo not in campos_calculados:
            print(f"AVISO: campo '{campo}' nao pode ser calculado. Pulando.")
            continue
        caminho_campo = inp_path.parent / f"{jobname}_{campo}.png"
        plotar_geometria_colorida_por_campo(
            dados["nodes"], campos_calculados[campo], campo, caminho_campo
        )
        print(f"OK: grafico de '{campo}' gerado -> {caminho_campo}")

    # Alem dos PNGs (que funcionam em qualquer PC), tenta abrir o CGX
    # nativo direto no .frd, mostrando a geometria deformada/colorida
    # pelos campos escolhidos -- igual o GIBIANE faz no Cast3M.
    # So roda se SHOW_MESH_CGX=True; se falhar por qualquer motivo, so
    # avisa e nao afeta os PNGs ja gerados.
    #
    # Quando o usuario escolhe "all", abrimos UMA janela de
    # deslocamento (comum a todos os campos) e DEPOIS uma janela de
    # tensao/deformacao PARA CADA campo escolhido -- cada abertura tem
    # seu proprio try/except, para que a falha em um campo especifico
    # (ex: Mises der erro) nao impeca as janelas dos demais campos de
    # serem abertas.
    if campos_escolhidos:
        #time.sleep(1)
        abrir_cgx_pos_processamento(frd_path, campos_escolhidos, fator)
        #time.sleep(1)

    print()
    print("=== Concluido ===")


#if __name__ == "__main__":
    #main_ccx(option21,qy_XOR_ux, fy_XOR_uy, fx_XOR_uz, mz, tx)