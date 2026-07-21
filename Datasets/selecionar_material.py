"""
selecionar_material.py

Funcao de selecao de material em arvore de 2 niveis, no mesmo estilo
da funcao "escolher_link()" fornecida como referencia (menu numerado +
match/case). 

NIVEL 1: categoria do material (aco, ferro fundido, titanio, aluminio,
         ou um material "simples" que ja tem 1 unico jogo de
         propriedades).
NIVEL 2: so aparece para categorias "compostas" (aco, ferro fundido,
         titanio, aluminio estrutural), porque essas variam muito
         demais para ter 1 unico valor de E/nu/etc.

Se o usuario escolher "outro" (ultima opcao do menu), ele digita
manualmente: E, nu, densidade, calor especifico, condutividade
termica e coeficiente de dilatacao.

Retorna sempre uma tupla padronizada:
    (nome_exibicao, E, nu, densidade, calor_especifico, k_termico, alpha)
"""

from materiais_db import MATERIAIS_SIMPLES, MATERIAIS_COMPOSTOS, MENU_NIVEL_1


def _ler_float(mensagem: str) -> float:
    """
    Pede um numero ao usuario repetidamente até receber um valor
    valido. Aceita virgula ou ponto como separador decimal.
    """
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            return float(bruto)
        except ValueError:
            print("Valor invalido. Digite um numero (ex: 210000 ou 210000.5).")


def _perguntar_propriedades_manual() -> tuple:
    """
    Usado quando o usuario escolhe "outro" -- pede cada propriedade
    do material manualmente, com a unidade esperada explicada.
    """
    print()
    print("Material 'outro' selecionado. Digite as propriedades abaixo.")
    print("(use ponto ou virgula como separador decimal)")
    print()

    nome = input("Nome do material (so para identificacao): ").strip()
    if not nome:
        nome = "Material customizado"

    E = _ler_float("Modulo de Young E [MPa]: ")
    nu = _ler_float("Coeficiente de Poisson nu [adimensional, ex: 0.3]: ")
    dens = _ler_float("Densidade [ton/mm^3, ex: 7.85e-9 para aco]: ")
    cp = _ler_float("Calor especifico cp [mJ/(ton.K), ex: 4.86e8 para aco]: ")
    k = _ler_float("Condutividade termica k [mW/(mm.K), ex: 50.0 para aco]: ")
    alpha = _ler_float("Coef. de dilatacao termica alpha [1/K, ex: 12.0e-6]: ")

    return (nome, E, nu, dens, cp, k, alpha)


def _exibir_submenu_composto(categoria_key: str, categoria_label: str) -> tuple:
    """
    Mostra o NIVEL 2: a lista de subtipos especificos dentro de uma
    categoria que varia muito (aco, ferro fundido, titanio, aluminio).
    """
    subtipos = MATERIAIS_COMPOSTOS[categoria_key]
    chaves = list(subtipos.keys())

    print()
    print(f"--- {categoria_label}: escolha o subtipo especifico ---")
    for i, chave in enumerate(chaves, start=1):
        nome_exibicao = subtipos[chave][0]
        print(f"{i} - {nome_exibicao}")
    print(f"{len(chaves) + 1} - Outro (digitar propriedades manualmente)")
    print()

    while True:
        opcao = input("Escolha o subtipo: ").strip()

        if opcao == str(len(chaves) + 1):
            return _perguntar_propriedades_manual()

        try:
            indice = int(opcao) - 1
            if 0 <= indice < len(chaves):
                chave_escolhida = chaves[indice]
                return subtipos[chave_escolhida]
        except ValueError:
            pass

        print("Opcao invalida, tente novamente.")


def selecionar_material() -> tuple:
    """
    Funcao principal de selecao de material, no mesmo espirito da
    funcao "escolher_link()" de referencia: imprime um menu numerado,
    le a opcao do usuario com match/case, e retorna o resultado.

    Retorna:
        tuple (nome, E[MPa], nu, densidade[ton/mm^3],
               calor_especifico[mJ/(ton.K)], k_termico[mW/(mm.K)],
               alpha[1/K])
    """
    print()
    print("=== Selecao de material ===")
    for i, (chave, label, tipo) in enumerate(MENU_NIVEL_1, start=1):
        print(f"{i} - {label}")
    opcao_outro = len(MENU_NIVEL_1) + 1
    print(f"{opcao_outro} - Outro (material nao listado, digitar tudo manualmente)")
    print()

    opcao = input("Escolha uma opcao: ").strip()

    # Usamos match/case sobre o INDICE numerico, igual ao estilo do
    # exemplo de referencia (escolher_link). Como o menu eh gerado
    # dinamicamente a partir de MENU_NIVEL_1, fazemos a comparacao
    # contra a posicao numerica calculada, nao contra strings fixas.
    match opcao:
        case op if op == str(opcao_outro):
            return _perguntar_propriedades_manual()

        case op if op.isdigit() and 1 <= int(op) <= len(MENU_NIVEL_1):
            indice = int(op) - 1
            chave, label, tipo = MENU_NIVEL_1[indice]

            if tipo == "composto":
                # Materiais que variam muito (aco, ferro fundido,
                # titanio, aluminio) -> abre o NIVEL 2.
                return _exibir_submenu_composto(chave, label)
            else:
                # Material "simples": 1 unico jogo de propriedades.
                return MATERIAIS_SIMPLES[chave]

        case _:
            print("Opcao invalida! Tente novamente.")
            return selecionar_material()


if __name__ == "__main__":
    # Teste manual rapido deste modulo isoladamente.
    resultado = selecionar_material()
    nome, E, nu, dens, cp, k, alpha = resultado
    print()
    print("=== Material selecionado ===")
    print(f"Nome  : {nome}")
    print(f"E     : {E} MPa")
    print(f"nu    : {nu}")
    print(f"dens  : {dens} ton/mm^3")
    print(f"cp    : {cp} mJ/(ton.K)")
    print(f"k     : {k} mW/(mm.K)")
    print(f"alpha : {alpha} 1/K")


def selecionar_material2() -> tuple:
    """
    Funcao principal de selecao de material, no mesmo espirito da
    funcao "escolher_link()" de referencia: imprime um menu numerado,
    le a opcao do usuario com match/case, e retorna o resultado.

    Retorna:
        tuple (nome, E[MPa], nu, densidade[ton/mm^3],
               calor_especifico[mJ/(ton.K)], k_termico[mW/(mm.K)],
               alpha[1/K])
    """
    lastr01 = ("escolha de material \n\n")
    straux2 = ""
    for i, (chave, label, tipo) in enumerate(MENU_NIVEL_1, start=1):
        lastr02 = (f"{straux2}\n{i} - {label}")
        straux2 = lastr02 
        
        
        
    opcao_outro = len(MENU_NIVEL_1) + 1
    lastr03 = (f"\n {opcao_outro} - Outro (material nao listado, digitar tudo manualmente)")
    
    
    #opcao = input("Escolha um desses materiais aqui: ").strip()
    lastr04 = ("Escolha um desses materiais aqui: ").strip()
    lastr05 = lastr01 + lastr02 + lastr03 + lastr04
    return lastr05
    opcao = 0#input("Escolha um desses materiais aqui: ").strip()
    
    
    # Usamos match/case sobre o INDICE numerico, igual ao estilo do
    # exemplo de referencia (escolher_link). Como o menu eh gerado
    # dinamicamente a partir de MENU_NIVEL_1, fazemos a comparacao
    # contra a posicao numerica calculada, nao contra strings fixas.
    match opcao:
        case op if op == str(opcao_outro):
            return _perguntar_propriedades_manual()

        case op if op.isdigit() and 1 <= int(op) <= len(MENU_NIVEL_1):
            indice = int(op) - 1
            chave, label, tipo = MENU_NIVEL_1[indice]

            if tipo == "composto":
                # Materiais que variam muito (aco, ferro fundido,
                # titanio, aluminio) -> abre o NIVEL 2.
                return _exibir_submenu_composto(chave, label)
            else:
                # Material "simples": 1 unico jogo de propriedades.
                return MATERIAIS_SIMPLES[chave]

        case _:
            print("Opcao invalida! Tente novamente.")
            return selecionar_material()

