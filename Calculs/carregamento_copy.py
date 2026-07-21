"""
carregamento.py

Define as condicoes de contorno e carregamento de uma barra/viga 1D
(elemento B31) no CalculiX, com a seguinte regra fixa:

    O ponto em x=0 (inicio da barra, primeiro no) e SEMPRE engastado
    (todos os graus de liberdade de translacao e rotacao bloqueados),
    independente da opcao escolhida pelo usuario.

O usuario escolhe um dos dois modos, mutuamente exclusivos:

    MODO "deslocamento": impoe o deslocamento final (u_final) no ultimo
        no da barra (extremidade em x=L). Nenhuma carga e aplicada.

    MODO "esforcos": impoe, nessa ordem:
        1) carga distribuida uniforme retangular ao longo de toda a
           barra (de 0 a L) -- usa *DLOAD do tipo P1 (carga
           perpendicular distribuida) em elementos B31.
        2) forca transversal concentrada no no final (x=L)
        3) forca axial concentrada no no final (x=L)
        4) momento fletor concentrado no no final (x=L)
        5) momento torçor concentrado no no final (x=L)

Retorna sempre uma lista de linhas de texto (.inp) prontas para
inserir no STEP do arquivo, alem de um dicionario-resumo (para exibir
ao usuario antes de confirmar).
"""


def _ler_float(mensagem: str, permitir_negativo: bool = True) -> float:
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(bruto)
            if not permitir_negativo and valor < 0:
                print("O valor nao pode ser negativo. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("Valor invalido. Digite um numero (ex: 1500.0 ou -250.5).")


def montar_engaste(node_id_inicio: int = 1) -> list[str]:
    """
    Monta o bloco *BOUNDARY que SEMPRE engasta totalmente o no inicial
    da barra (x=0): bloqueia translacoes (1,2,3) e rotacoes (4,5,6),
    ja que estamos usando elemento de viga B31 (6 graus de liberdade
    por no).
    """
    return [
        "*BOUNDARY",
        f"{node_id_inicio}, 1, 6, 0.0",
    ]


def _definir_deslocamento_imposto_v0(node_id_final: int,qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0) -> tuple[list[str], dict]:
    qy_XOR_ux = float(qy_XOR_ux)
    fy_XOR_uy = float(fy_XOR_uy)
    fx_XOR_uz = float(fx_XOR_uz)
    
    ux2 = qy_XOR_ux*qy_XOR_ux
    uy2 = fy_XOR_uy*fy_XOR_uy
    uz2 = fx_XOR_uz*fx_XOR_uz
    print()
    print("=== Modo: impor DESLOCAMENTO no no final ===")
    
    print(f"O no final (no {node_id_final}, em x=L) tera deslocamento imposto.")

    print("Digite os componentes do deslocamento final (em mm). Deixe 0 se nao aplicavel.")

    ux = _ler_float("u_final em X (axial) [mm]: ")

    uy = _ler_float("u_final em Y (transversal) [mm]: ")

    uz = _ler_float("u_final em Z (transversal) [mm]: ")

    if((ux2+uy2+uz2)==0):
        ux = ux#qy_XOR_ux*qy_XOR_ux
        uy = uy#fy_XOR_uy*fy_XOR_uy
        uz = uz#fx_XOR_uz*fx_XOR_uz    
    else:
        ux = qy_XOR_ux#*qy_XOR_ux
        uy = fy_XOR_uy#*fy_XOR_uy
        uz = fx_XOR_uz#*fx_XOR_uz
    

    linhas = [
        "*BOUNDARY",
        f"{node_id_final}, 1, 1, {ux}",
        f"{node_id_final}, 2, 2, {uy}",
        f"{node_id_final}, 3, 3, {uz}",
    ]

    resumo = {
        "modo": "deslocamento",
        "u_final": (ux, uy, uz),
    }
    return linhas, resumo


def _definir_deslocamento_imposto(node_id_final: int,qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0):
    # -> tuple[list[str], dict]:
    qy_XOR_ux = float(qy_XOR_ux)
    fy_XOR_uy = float(fy_XOR_uy)
    fx_XOR_uz = float(fx_XOR_uz)
    
    ux2 = qy_XOR_ux*qy_XOR_ux
    uy2 = fy_XOR_uy*fy_XOR_uy
    uz2 = fx_XOR_uz*fx_XOR_uz
    print()
    #print("=== Modo: impor DESLOCAMENTO no no final ===")
    
    #print(f"O no final (no {node_id_final}, em x=L) tera deslocamento imposto.")

    print("Digite os componentes do deslocamento final (em mm). Deixe 0 se nao aplicavel.")

    #ux# = _ler_float("u_final em X (axial) [mm]: ")

    #uy# = _ler_float("u_final em Y (transversal) [mm]: ")

    #uz# = _ler_float("u_final em Z (transversal) [mm]: ")

    if((ux2+uy2+uz2)==0):
        ux = 0#qy_XOR_ux*qy_XOR_ux
        uy = 0#fy_XOR_uy*fy_XOR_uy
        uz = 0#fx_XOR_uz*fx_XOR_uz    
    else:
        ux = qy_XOR_ux#*qy_XOR_ux
        uy = fy_XOR_uy#*fy_XOR_uy
        uz = fx_XOR_uz#*fx_XOR_uz
    

    linhas = [
        "*BOUNDARY",
        f"{node_id_final}, 1, 1, {ux}",
        f"{node_id_final}, 2, 2, {uy}",
        f"{node_id_final}, 3, 3, {uz}",
    ]

    resumo = {
        "modo": "deslocamento",
        "u_final": (ux, uy, uz),
    }
    return linhas, resumo



def _definir_esforcos_v0(node_id_final: int, elset: str = "BARRA",qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0, mz=0, tx=0)-> tuple[list[str], dict]:
    qy_XOR_ux = float(qy_XOR_ux)
    fy_XOR_uy = float(fy_XOR_uy)
    fx_XOR_uz = float(fx_XOR_uz)
    mz = float(mz)
    tx = float(tx)
    
    ux2 = qy_XOR_ux*qy_XOR_ux
    uy2 = fy_XOR_uy*fy_XOR_uy
    uz2 = fx_XOR_uz*fx_XOR_uz
    mz2 = mz*mz
    tx2 = tx*tx
    
    ux = qy_XOR_ux#*qy_XOR_ux
    uy = fy_XOR_uy#*fy_XOR_uy
    uz = fx_XOR_uz#*fx_XOR_uz
    mz = mz#*mz
    tx = tx#*tx
    
    print()
    print("=== Modo: impor ESFORCOS ===")

    print("Os esforcos sao aplicados na seguinte ordem fixa:")

    print("  1) Carga distribuida uniforme (retangular) ao longo de toda a barra")
    print("  2) Forca transversal concentrada no no final")
    print("  3) Forca axial concentrada no no final")
    print("  4) Momento fletor concentrado no no final")
    print("  5) Momento torçor concentrado no no final")

    print()
    print("Digite 0 para qualquer esforco que nao se aplique ao seu caso.")
    print()


    print("--- 1) Carga distribuida uniforme (0 a L) ---")
    q_dist = _ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
    print()
    print("--- 2) Forca transversal no no final ---")
    f_transversal = _ler_float("Forca transversal F [N] (eixo Y local): ")
    print()
    print("--- 3) Forca axial no no final ---")
    f_axial = _ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
    print()
    print("--- 4) Momento fletor no no final ---")
    m_fletor = _ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
    print()
    print("--- 5) Momento torçor no no final ---")
    m_torcor = _ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")

    if((ux2+uy2+uz2+mz2+tx2)==0):
        print("--- 1) Carga distribuida uniforme (0 a L) ---")
        q_dist = q_dist# _ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
        print()
        print("--- 2) Forca transversal no no final ---")
        f_transversal = f_transversal#_ler_float("Forca transversal F [N] (eixo Y local): ")
        print()
        print("--- 3) Forca axial no no final ---")
        f_axial = f_axial#_ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
        print()
        print("--- 4) Momento fletor no no final ---")
        m_fletor = m_fletor#_ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
        print()
        print("--- 5) Momento torçor no no final ---")
        m_torcor = m_torcor#_ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")
    else:
        print("--- 1) Carga distribuida uniforme (0 a L) ---")
        q_dist = ux#_ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
        print()
        print("--- 2) Forca transversal no no final ---")
        f_transversal = uy#_ler_float("Forca transversal F [N] (eixo Y local): ")
        print()
        print("--- 3) Forca axial no no final ---")
        f_axial = uz#_ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
        print()
        print("--- 4) Momento fletor no no final ---")
        m_fletor = mz#_ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
        print()
        print("--- 5) Momento torçor no no final ---")
        m_torcor = tx#_ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")


    linhas = []

    if q_dist != 0.0:
        # *DLOAD com tipo P1: carga distribuida perpendicular ao eixo da
        # viga, uniforme em toda a extensao do elemento. Aplicada a
        # TODOS os elementos do ELSET (cobre 0 a L de forma retangular).
        linhas.append("*DLOAD")
        linhas.append(f"{elset}, P1, {q_dist}")

    cload_linhas = []
    if f_transversal != 0.0:
        cload_linhas.append(f"{node_id_final}, 2, {f_transversal}")
    if f_axial != 0.0:
        cload_linhas.append(f"{node_id_final}, 1, {f_axial}")
    if m_fletor != 0.0:
        cload_linhas.append(f"{node_id_final}, 6, {m_fletor}")
    if m_torcor != 0.0:
        cload_linhas.append(f"{node_id_final}, 4, {m_torcor}")

    if cload_linhas:
        linhas.append("*CLOAD")
        linhas.extend(cload_linhas)

    resumo = {
        "modo": "esforcos",
        "q_distribuida": q_dist,
        "forca_transversal": f_transversal,
        "forca_axial": f_axial,
        "momento_fletor": m_fletor,
        "momento_torçor": m_torcor,
    }
    return linhas, resumo

def _definir_esforcos(node_id_final: int, elset: str = "BARRA",qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0, mz=0, tx=0):
    #-> tuple[list[str], dict]:
    qy_XOR_ux = float(qy_XOR_ux)
    fy_XOR_uy = float(fy_XOR_uy)
    fx_XOR_uz = float(fx_XOR_uz)
    mz = float(mz)
    tx = float(tx)
    
    ux2 = qy_XOR_ux*qy_XOR_ux
    uy2 = fy_XOR_uy*fy_XOR_uy
    uz2 = fx_XOR_uz*fx_XOR_uz
    mz2 = mz*mz
    tx2 = tx*tx
    
    ux = qy_XOR_ux#*qy_XOR_ux
    uy = fy_XOR_uy#*fy_XOR_uy
    uz = fx_XOR_uz#*fx_XOR_uz
    mz = mz#*mz
    tx = tx#*tx
    
    print()
    print("=== Modo: impor ESFORCOS ===")

    print("Os esforcos sao aplicados na seguinte ordem fixa:")

    print("  1) Carga distribuida uniforme (retangular) ao longo de toda a barra")
    print("  2) Forca transversal concentrada no no final")
    print("  3) Forca axial concentrada no no final")
    print("  4) Momento fletor concentrado no no final")
    print("  5) Momento torçor concentrado no no final")

    print()
    print("Digite 0 para qualquer esforco que nao se aplique ao seu caso.")
    print()


    print("--- 1) Carga distribuida uniforme (0 a L) ---")
    #q_dist# = _ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
    print()
    print("--- 2) Forca transversal no no final ---")
    #f_transversal# = _ler_float("Forca transversal F [N] (eixo Y local): ")
    print()
    print("--- 3) Forca axial no no final ---")
    #f_axial# = _ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
    print()
    print("--- 4) Momento fletor no no final ---")
    #m_fletor# = _ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
    print()
    print("--- 5) Momento torçor no no final ---")
    #m_torcor# = _ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")

    if((ux2+uy2+uz2+mz2+tx2)==0):
        print("--- 1) Carga distribuida uniforme (0 a L) ---")
        q_dist = 0#q_dist# _ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
        print()
        print("--- 2) Forca transversal no no final ---")
        f_transversal = 0#f_transversal#_ler_float("Forca transversal F [N] (eixo Y local): ")
        print()
        print("--- 3) Forca axial no no final ---")
        f_axial = 0#f_axial#_ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
        print()
        print("--- 4) Momento fletor no no final ---")
        m_fletor = 0#m_fletor#_ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
        print()
        print("--- 5) Momento torçor no no final ---")
        m_torcor = 0#m_torcor#_ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")
    else:
        print("--- 1) Carga distribuida uniforme (0 a L) ---")
        q_dist = ux#_ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")
        print()
        print("--- 2) Forca transversal no no final ---")
        f_transversal = uy#_ler_float("Forca transversal F [N] (eixo Y local): ")
        print()
        print("--- 3) Forca axial no no final ---")
        f_axial = uz#_ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")
        print()
        print("--- 4) Momento fletor no no final ---")
        m_fletor = mz#_ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")
        print()
        print("--- 5) Momento torçor no no final ---")
        m_torcor = tx#_ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")


    linhas = []

    if q_dist != 0.0:
        # *DLOAD com tipo P1: carga distribuida perpendicular ao eixo da
        # viga, uniforme em toda a extensao do elemento. Aplicada a
        # TODOS os elementos do ELSET (cobre 0 a L de forma retangular).
        linhas.append("*DLOAD")
        linhas.append(f"{elset}, P1, {q_dist}")

    cload_linhas = []
    if f_transversal != 0.0:
        cload_linhas.append(f"{node_id_final}, 2, {f_transversal}")
    if f_axial != 0.0:
        cload_linhas.append(f"{node_id_final}, 1, {f_axial}")
    if m_fletor != 0.0:
        cload_linhas.append(f"{node_id_final}, 6, {m_fletor}")
    if m_torcor != 0.0:
        cload_linhas.append(f"{node_id_final}, 4, {m_torcor}")

    if cload_linhas:
        linhas.append("*CLOAD")
        linhas.extend(cload_linhas)

    resumo = {
        "modo": "esforcos",
        "q_distribuida": q_dist,
        "forca_transversal": f_transversal,
        "forca_axial": f_axial,
        "momento_fletor": m_fletor,
        "momento_torçor": m_torcor,
    }
    return linhas, resumo



def definir_carregamento_v0(node_id_inicio: int, node_id_final: int, elset: str = "BARRA",option21=0,qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0, mz=0, tx=0) -> tuple[list[str], dict]:
    """
    Funcao principal: pergunta ao usuario se quer impor deslocamento ou
    esforcos, monta as linhas de .inp correspondentes, e SEMPRE inclui
    o engaste no no inicial.

    Retorna (lista_de_linhas_inp, dicionario_resumo).
    """
    print()
    print("=== Definicao do carregamento ===")
    
    print(f"O no {node_id_inicio} (x=0) sera SEMPRE engastado (todos os DOFs bloqueados).")
    
    print()
    print("1 - Impor DESLOCAMENTO no no final (u_final)")
    
    print("2 - Impor ESFORCOS (carga distribuida + forcas + momentos no no final)")
    
    print()

    opcao = input("Escolha uma opcao: ").strip()

    if(option21==0):
        opcao = opcao
    else:
        opcao = f"{option21}"

    linhas_engaste = montar_engaste(node_id_inicio)

    match opcao:
        case "1":
            linhas_carga, resumo = _definir_deslocamento_imposto(node_id_final,qy_XOR_ux, fy_XOR_uy, fx_XOR_uz) 
        case "2":
            linhas_carga, resumo = _definir_esforcos(node_id_final, elset, qy_XOR_ux, fy_XOR_uy, fx_XOR_uz, mz, tx)
        case _:
            print("Opcao invalida! Tente novamente.")
            return definir_carregamento(node_id_inicio, node_id_final, elset,option21=0)

    linhas_finais = linhas_engaste + linhas_carga
    return linhas_finais, resumo


def definir_carregamento(node_id_inicio: int, node_id_final: int, elset: str = "BARRA",option21=0,qy_XOR_ux=0, fy_XOR_uy=0, fx_XOR_uz=0, mz=0, tx=0):
    #-> tuple[list[str], dict]:
    """
    Funcao principal: pergunta ao usuario se quer impor deslocamento ou
    esforcos, monta as linhas de .inp correspondentes, e SEMPRE inclui
    o engaste no no inicial.

    Retorna (lista_de_linhas_inp, dicionario_resumo).
    """
    print()
    print("=== Definicao do carregamento ===")
    
    print(f"O no {node_id_inicio} (x=0) sera SEMPRE engastado (todos os DOFs bloqueados).")
    
    print()
    print("1 - Impor DESLOCAMENTO no no final (u_final)")
    
    print("2 - Impor ESFORCOS (carga distribuida + forcas + momentos no no final)")
    
    print()

    #opcao# = input("Escolha uma opcao: ").strip()

    if(option21==0):
        #opcao# = opcao
        print("...")
    else:
        opcao = f"{option21}"

    linhas_engaste = montar_engaste(node_id_inicio)

    match opcao:
        case "1":
            linhas_carga, resumo = _definir_deslocamento_imposto(node_id_final,qy_XOR_ux, fy_XOR_uy, fx_XOR_uz) 
        case "2":
            linhas_carga, resumo = _definir_esforcos(node_id_final, elset, qy_XOR_ux, fy_XOR_uy, fx_XOR_uz, mz, tx)
        case _:
            print("Opcao invalida! Tente novamente.")
            return definir_carregamento(node_id_inicio, node_id_final, elset,option21=0)

    linhas_finais = linhas_engaste + linhas_carga
    return linhas_finais, resumo


if __name__ == "__main__":
    linhas, resumo = definir_carregamento(node_id_inicio=1, node_id_final=5)
    print()
    print("=== Linhas .inp geradas ===")
    print("\n".join(linhas))
    print()
    print("=== Resumo ===")
    print(resumo)
