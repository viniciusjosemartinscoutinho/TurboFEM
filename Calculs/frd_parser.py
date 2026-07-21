"""
frd_parser.py

Parser Python puro (sem vtk, sem dependencias pesadas) do arquivo de
resultados ASCII do CalculiX (.frd).

O algoritmo de leitura (regex de colunas fixas, nomes de bloco, ordem
dos campos) e baseado no parser OFICIAL do projeto calculix/ccx2paraview
(licenca GPL-3.0, (c) Ihor Mirzov), que e o conversor de referencia
mantido pelo proprio time do CalculiX. Aqui reimplementamos so a parte
de LEITURA (sem a parte de escrita para VTK/Paraview), em Python puro.

Blocos suportados:
    "2"   -> bloco de coordenadas dos nos
    "3"   -> bloco de definicao dos elementos (nao usado neste script,
             mas reconhecido para nao confundir o parser)
    "100" -> bloco de resultados (DISP, STRESS, etc.) de um incremento

Retorna um dicionario:
    {
        "nodes": {node_id: (x, y, z), ...},
        "disp":  {node_id: (ux, uy, uz), ...},
        "stress": {node_id: (sxx, syy, szz, sxy, syz, szx), ...},
    }
"""

import re


def _match_line(regex: str, line: str):
    match = re.search(regex, line)
    if not match:
        raise SyntaxError(f"Nao foi possivel interpretar a linha do .frd:\n{line!r}\ncom regex: {regex}")
    return match


_REGEX_NUMERO = re.compile(r'[+-]?\d\.\d+E[+-]\d{2,3}')


def _extrair_numeros(texto: str) -> list[float]:
    """
    Extrai todos os numeros em notacao cientifica de uma string,
    independente de quantos espacos existem entre eles ou de colarem
    um no outro sem espaco (ex: "1.0E+02-5.0E+02" -> dois numeros).

    Usar isso em vez de largura fixa de coluna evita os problemas de
    parsing observados entre diferentes versoes/plataformas do CCX,
    onde a largura exata do campo (numero de digitos do expoente,
    presenca ou nao de espaco antes do sinal negativo) pode variar.
    """
    return [float(m) for m in _REGEX_NUMERO.findall(texto)]


def _parse_node_block(linhas: list[str], indice: int) -> tuple[dict, int]:
    """
    Le o bloco de coordenadas dos nos (chave '2' / '-1' por linha).
    Retorna (dict_nos, indice_apos_o_bloco).
    """
    nodes = {}
    i = indice

    while i < len(linhas):
        linha = linhas[i].rstrip("\n")
        if linha.strip() == "-3" or linha.strip() == "":
            i += 1
            break
        if not linha.strip().startswith("-1"):
            i += 1
            continue

        # O node_id vem entre o "-1" inicial e o primeiro numero em
        # notacao cientifica (ele mesmo e um inteiro simples, sem ponto
        # decimal nem E, entao nao e capturado por _extrair_numeros).
        match_id = re.search(r'^\s*-1\s*(\d+?)(?=\s*[+-]?\d\.\d+E[+-]\d{2,3})', linha)
        if not match_id:
            raise SyntaxError(f"Nao foi possivel ler o ID do no na linha:\n{linha!r}")
        node_id = int(match_id.group(1))

        coords = _extrair_numeros(linha)
        if len(coords) < 3:
            raise SyntaxError(f"Esperava 3 coordenadas na linha de no, achei {len(coords)}:\n{linha!r}")

        x, y, z = coords[0], coords[1], coords[2]
        nodes[node_id] = (x, y, z)
        i += 1

    return nodes, i


def _read_vars_info(linha: str) -> tuple[str, int]:
    """
    Le a linha '-4  DISP   4   1' / '-4  STRESS  6   1' etc.
    Retorna (nome_da_variavel, numero_de_componentes).
    """
    regex = r'^\s*-4\s+(\w+)' + r'\D+(\d+)' * 2
    match = _match_line(regex, linha.rstrip("\n"))
    nome = match.group(1)
    ncomps = int(match.group(2))

    # Normaliza nomes para os nomes usados no .inp (igual ao ccx2paraview)
    nomes_normalizados = {
        "DISP": "U",
        "STRESS": "S",
        "TOSTRAIN": "E",
        "FORC": "RF",
    }
    nome = nomes_normalizados.get(nome, nome)
    return nome, ncomps


def _parse_results_block(linhas: list[str], indice: int) -> tuple[str, dict, int]:
    """
    Le um bloco de resultados completo: cabecalho de variavel (-4),
    nomes dos componentes (-5, um por componente) e os valores por no
    (-1 e continuacoes -2).

    Retorna (nome_da_variavel, dict_de_resultados_por_no, indice_apos_o_bloco).
    """
    i = indice
    nome, ncomps_bruto = _read_vars_info(linhas[i])
    i += 1

    # Le as linhas de definicao de componentes (-5 ...). Uma delas pode
    # ser "ALL" (componente calculada/agregada, nao um valor armazenado
    # de fato) -- quando isso acontece, o numero REAL de componentes
    # armazenados e ncomps_bruto - 1. Replicamos a logica do
    # ccx2paraview original: ler ncomps_bruto linhas de definicao, mas
    # decrementar a contagem real sempre que uma delas contiver "ALL".
    ncomps_reais = ncomps_bruto
    for _ in range(ncomps_bruto):
        linha_comp = linhas[i]
        if "ALL" in linha_comp:
            ncomps_reais -= 1
        i += 1

    resultados = {}
    row_comps_total = min(6, ncomps_reais)

    while i < len(linhas):
        linha = linhas[i].rstrip("\n")
        if linha.strip() == "-3" or linha.strip() == "":
            i += 1
            break

        if not linha.strip().startswith("-1"):
            # Nao e mais uma linha de resultado -- bloco terminou.
            break

        match_id = re.search(r'^\s*-1\s*(\d+?)(?=\s*[+-]?\d\.\d+E[+-]\d{2,3})', linha)
        if not match_id:
            raise SyntaxError(f"Nao foi possivel ler o ID do no na linha de resultado:\n{linha!r}")
        node_id = int(match_id.group(1))

        valores = _extrair_numeros(linha)
        if len(valores) < row_comps_total:
            raise SyntaxError(
                f"Esperava {row_comps_total} valores na linha de resultado, "
                f"achei {len(valores)}:\n{linha!r}"
            )
        valores = valores[:row_comps_total]
        i += 1

        # Continuacao em linha(s) "-2" se houver mais de 6 componentes
        # reais (caso de STRESS com 6 componentes isso nao acontece,
        # mas deixamos generico para outros casos futuros).
        restantes = ncomps_reais - row_comps_total
        while restantes > 0:
            linha_cont = linhas[i].rstrip("\n")
            row_comps_cont = min(6, restantes)
            valores_cont = _extrair_numeros(linha_cont)[:row_comps_cont]
            valores.extend(valores_cont)
            restantes -= row_comps_cont
            i += 1

        resultados[node_id] = tuple(valores)

    return nome, resultados, i


def parse_frd(caminho_frd) -> dict:
    """
    Le um arquivo .frd ASCII do CalculiX e retorna um dicionario com
    nodes, disp, stress e strain (os ultimos tres podem vir vazios se
    o .frd nao contiver esses campos).
    """
    texto = caminho_frd.read_text(encoding="utf-8", errors="replace")
    linhas = texto.split("\n")

    nodes = {}
    disp = {}
    stress = {}
    strain = {}

    i = 0
    while i < len(linhas):
        linha = linhas[i]
        chave = linha[:5].strip()

        if chave == "2":
            nodes, i = _parse_node_block(linhas, i + 1)
            continue

        if chave == "100":
            # Dentro de um bloco "100" pode vir DISP, depois STRESS,
            # TOSTRAIN, etc., cada um com seu proprio sub-cabecalho "-4".
            i += 1
            while i < len(linhas) and linhas[i].strip().startswith("-4"):
                nome, resultados, i = _parse_results_block(linhas, i)
                if nome == "U":
                    disp = resultados
                elif nome == "S":
                    stress = resultados
                elif nome == "E":
                    strain = resultados
            continue

        if chave == "9999":
            break

        i += 1

    return {"nodes": nodes, "disp": disp, "stress": stress, "strain": strain}


def calcular_von_mises(stress_tupla: tuple) -> float:
    """
    Calcula a tensao equivalente de von Mises a partir do tensor de
    tensoes (sxx, syy, szz, sxy, syz, szx), exatamente como o
    ccx2paraview oficial faz.
    """
    sxx, syy, szz, sxy, syz, szx = stress_tupla
    return (1 / (2 ** 0.5)) * (
        (sxx - syy) ** 2
        + (syy - szz) ** 2
        + (szz - sxx) ** 2
        + 6 * syz ** 2
        + 6 * szx ** 2
        + 6 * sxy ** 2
    ) ** 0.5


def calcular_tensoes_principais(stress_tupla: tuple) -> tuple[float, float, float]:
    """
    Calcula as 3 tensoes principais (autovalores do tensor de tensao
    3x3), sem depender de numpy -- usa a formula analitica classica
    para autovalores de uma matriz simetrica 3x3 (formula trigonometrica
    de Cardano para matrizes simetricas).

    Retorna (sigma_min, sigma_mid, sigma_max).
    """
    sxx, syy, szz, sxy, syz, szx = stress_tupla

    # Invariantes do tensor
    I1 = sxx + syy + szz
    I2 = (sxx * syy + syy * szz + szz * sxx) - (sxy ** 2 + syz ** 2 + szx ** 2)
    I3 = (
        sxx * syy * szz
        + 2 * sxy * syz * szx
        - sxx * syz ** 2
        - syy * szx ** 2
        - szz * sxy ** 2
    )

    # Metodo trigonometrico para autovalores de matriz simetrica 3x3
    # (evita dependencia de numpy.linalg.eigvals).
    m = I1 / 3.0
    q = (
        (sxx - m) * (syy - m) * (szz - m)
        + 2 * sxy * syz * szx
        - (sxx - m) * syz ** 2
        - (syy - m) * szx ** 2
        - (szz - m) * sxy ** 2
    ) / 2.0
    p = (
        (sxx - m) ** 2 + (syy - m) ** 2 + (szz - m) ** 2
        + 2 * (sxy ** 2 + syz ** 2 + szx ** 2)
    ) / 6.0

    if p <= 1e-12:
        # Tensor aproximadamente esferico (hidrostatico) -- os 3
        # autovalores sao praticamente iguais a m.
        return (m, m, m)

    phi_arg = max(-1.0, min(1.0, q / (p ** 1.5)))
    phi = __import__("math").acos(phi_arg) / 3.0

    sqrt_p = p ** 0.5
    pi = __import__("math").pi

    eig1 = m + 2 * sqrt_p * __import__("math").cos(phi)
    eig2 = m + 2 * sqrt_p * __import__("math").cos(phi + (2 * pi / 3))
    eig3 = m + 2 * sqrt_p * __import__("math").cos(phi + (4 * pi / 3))

    autovalores = sorted([eig1, eig2, eig3])
    return (autovalores[0], autovalores[1], autovalores[2])


def calcular_deformacoes_principais(strain_tupla: tuple) -> tuple[float, float, float]:
    """
    Calcula as 3 deformacoes principais (autovalores do tensor de
    deformacao 3x3), usando a mesma formula trigonometrica de
    calcular_tensoes_principais -- o tensor de deformacao do CalculiX
    (TOSTRAIN) vem nas mesmas 6 componentes (EXX,EYY,EZZ,EXY,EYZ,EZX),
    entao a matematica de autovalores e identica, so o significado
    fisico muda (deformacao em vez de tensao).

    Retorna (epsilon_min, epsilon_mid, epsilon_max).
    """
    return calcular_tensoes_principais(strain_tupla)


def calcular_tresca(stress_tupla: tuple) -> float:
    """
    Calcula a tensao equivalente de Tresca: diferenca entre a maior e
    a menor tensao principal.
    """
    sigma_min, _, sigma_max = calcular_tensoes_principais(stress_tupla)
    return sigma_max - sigma_min