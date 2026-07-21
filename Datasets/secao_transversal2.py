"""
secao_transversal.py

Define a area da secao transversal e os momentos de inercia (flexao em
dois eixos + torcao) de uma barra/viga 1D, de duas formas possiveis:

    OPCAO A: escolher um perfil padrao (retangular, circular cheio,
             circular tubular, tipo I) e o script calcula A, Iy, Iz e
             J automaticamente a partir das dimensoes.

    OPCAO B: digitar A, Iy, Iz e J diretamente (uso quando a secao ja
             foi calculada em outro lugar, ou e uma secao customizada).

Convencao de eixos (igual ao CalculiX *BEAM SECTION):
    eixo 1 (local) = eixo da barra (longitudinal)
    eixo 2 e 3 (locais) = eixos da secao transversal
    Iy = momento de inercia em torno do eixo 2 (flexao em um plano)
    Iz = momento de inercia em torno do eixo 3 (flexao no plano perpendicular)
    J  = momento de inercia polar / constante de torcao

Unidades: mm para comprimento -> A em mm^2, I/J em mm^4.
"""

import math


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


def _secao_retangular() -> dict:
    print()
    print("Secao RETANGULAR -- digite base e altura em mm.")
    b = _ler_float("Base  b [mm]: ")
    h = _ler_float("Altura h [mm]: ")

    A = b * h
    Iy = (b * h**3) / 12.0   # flexao em torno do eixo que faz a altura "h" trabalhar
    Iz = (h * b**3) / 12.0   # flexao em torno do eixo que faz a base "b" trabalhar

    # Constante de torcao para secao rectangular (aproximacao classica
    # de Saint-Venant para retangulo estreito/largo -- formula de Roark).
    a = max(b, h) / 2.0
    bb = min(b, h) / 2.0
    if a > 0:
        J = a * bb**3 * (16.0 / 3.0 - 3.36 * (bb / a) * (1 - (bb**4) / (12.0 * a**4)))
    else:
        J = 0.0

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": f"Retangular {b}x{h} mm"}

def _secao_retangular2( b, h) -> dict:
    
    #sr1 = ("Secao RETANGULAR -- digite base e altura em mm.")
    #b = _ler_float("Base  b [mm]: ")
    #h = _ler_float("Altura h [mm]: ")

    A = b * h
    Iy = (b * h**3) / 12.0   # flexao em torno do eixo que faz a altura "h" trabalhar
    Iz = (h * b**3) / 12.0   # flexao em torno do eixo que faz a base "b" trabalhar

    # Constante de torcao para secao rectangular (aproximacao classica
    # de Saint-Venant para retangulo estreito/largo -- formula de Roark).
    a = max(b, h) / 2.0
    bb = min(b, h) / 2.0
    if a > 0:
        J = a * bb**3 * (16.0 / 3.0 - 3.36 * (bb / a) * (1 - (bb**4) / (12.0 * a**4)))
    else:
        J = 0.0

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": f"Retangular {b}x{h} mm"}

def _secao_circular_cheia() -> dict:
    print()
    print("Secao CIRCULAR CHEIA -- digite o diametro em mm.")
    d = _ler_float("Diametro d [mm]: ")
    r = d / 2.0

    A = math.pi * r**2
    Iy = Iz = (math.pi * d**4) / 64.0
    J = (math.pi * d**4) / 32.0   # = Iy + Iz, polar para secao circular cheia

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": f"Circular cheia d={d} mm"}

def _secao_circular_cheia2(d) -> dict:
    
    sc1 = ("Seção circular compacta... \nDigite o diâmetro em [mm].")
    #d = _ler_float("Diametro d [mm]: ")
    r = d / 2.0

    A = math.pi * r**2
    Iy = Iz = (math.pi * d**4) / 64.0
    J = (math.pi * d**4) / 32.0   # = Iy + Iz, polar para secao circular cheia

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": f"Circular cheia d={d} mm"}


def _secao_circular_tubular() -> dict:
    print()
    print("Secao CIRCULAR TUBULAR (tubo) -- digite diametro externo e interno em mm.")
    d_ext = _ler_float("Diametro externo D [mm]: ")
    d_int = _ler_float("Diametro interno d [mm]: ")

    if d_int >= d_ext:
        print("AVISO: diametro interno maior ou igual ao externo nao faz sentido.")
        print("Usando diametro interno = 0 (secao cheia) como fallback seguro.")
        d_int = 0.0

    A = (math.pi / 4.0) * (d_ext**2 - d_int**2)
    Iy = Iz = (math.pi / 64.0) * (d_ext**4 - d_int**4)
    J = (math.pi / 32.0) * (d_ext**4 - d_int**4)

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J,
            "descricao": f"Tubular D={d_ext} mm / d={d_int} mm"}


def _secao_circular_tubular2(d_ext, d_int) -> dict:
    
    #d_ext = _ler_float("Diametro externo D [mm]: ")
    #d_int = _ler_float("Diametro interno d [mm]: ")
    sct01 = ("Seção circular tubular (tubo)...\n  diâmetro externo e interno em [mm].\n\n")
    sct02 = ("Diâmetro externo D em [mm]: ")
    sct03 = ("Diâmetro interno d em [mm]: ")
    
    

    if d_int >= d_ext:
        print("AVISO: diametro interno maior ou igual ao externo nao faz sentido.")
        print("Usando diametro interno = 0 (secao cheia) como fallback seguro.")
        d_int = 0.0

    A = (math.pi / 4.0) * (d_ext**2 - d_int**2)
    Iy = Iz = (math.pi / 64.0) * (d_ext**4 - d_int**4)
    J = (math.pi / 32.0) * (d_ext**4 - d_int**4)

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J,
            "descricao": f"Tubular D={d_ext} mm / d={d_int} mm"}


def _secao_perfil_i() -> dict:
    print()
    print("Secao tipo I (viga I simplificada, mesas + alma) -- dimensoes em mm.")
    print("    largura da mesa (bf), altura total (h), espessura da mesa (tf),")
    print("    espessura da alma (tw)")
    bf = _ler_float("Largura da mesa bf [mm]: ")
    h = _ler_float("Altura total h [mm]: ")
    tf = _ler_float("Espessura da mesa tf [mm]: ")
    tw = _ler_float("Espessura da alma tw [mm]: ")

    hw = h - 2 * tf  # altura livre da alma, entre as mesas

    # Area: 2 mesas + alma
    A = 2 * (bf * tf) + (hw * tw)

    # Momento de inercia em torno do eixo forte (Iy, flexao "normal" de viga I):
    # soma de mesas (Teorema dos eixos paralelos) + alma.
    Iy = (
        2 * ((bf * tf**3) / 12.0 + bf * tf * ((h - tf) / 2.0) ** 2)
        + (tw * hw**3) / 12.0
    )

    # Momento de inercia em torno do eixo fraco (Iz, flexao lateral):
    Iz = 2 * ((tf * bf**3) / 12.0) + (hw * tw**3) / 12.0

    # Constante de torcao aproximada para perfil I (soma de retangulos
    # finos -- aproximacao classica de Saint-Venant para secoes abertas
    # de paredes finas).
    J = (1.0 / 3.0) * (2 * bf * tf**3 + hw * tw**3)

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J,
            "descricao": f"Perfil I bf={bf} h={h} tf={tf} tw={tw} mm"}


def _secao_perfil_i2(bf, h, tf, tw) -> dict:
    istr1 = ("Secao tipo I (viga I simplificada)...\n dimensões em [mm].\n\n")
    istr2 = ("\n largura (bf), altura total (h), espessura1(tf),")
    istr3 = ("\n espessura2 (tw)\n\n")
    istr4 = ("Largura da mesa bf [mm]: ")
    istr5 = istr1 + istr2 + istr3 + istr4
    
    #bf = _ler_float("Largura da mesa bf [mm]: ")
    #h = _ler_float("Altura total h [mm]: ")
    #tf = _ler_float("Espessura da mesa tf [mm]: ")
    #tw = _ler_float
    # ("Espessura da alma tw [mm]: ")

    hw = h - 2 * tf  # altura livre da alma, entre as mesas

    # Area: 2 mesas + alma
    A = 2 * (bf * tf) + (hw * tw)

    # Momento de inercia em torno do eixo forte (Iy, flexao "normal" de viga I):
    # soma de mesas (Teorema dos eixos paralelos) + alma.
    Iy = (
        2 * ((bf * tf**3) / 12.0 + bf * tf * ((h - tf) / 2.0) ** 2)
        + (tw * hw**3) / 12.0
    )

    # Momento de inercia em torno do eixo fraco (Iz, flexao lateral):
    Iz = 2 * ((tf * bf**3) / 12.0) + (hw * tw**3) / 12.0

    # Constante de torcao aproximada para perfil I (soma de retangulos
    # finos -- aproximacao classica de Saint-Venant para secoes abertas
    # de paredes finas).
    J = (1.0 / 3.0) * (2 * bf * tf**3 + hw * tw**3)

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J,
            "descricao": f"Perfil I bf={bf} h={h} tf={tf} tw={tw} mm"}


def _secao_valores_diretos() -> dict:
    print()
    print("Digitando A, Iy, Iz e J diretamente (em mm^2 e mm^4).")
    A = _ler_float("Area da secao A [mm^2]: ")
    Iy = _ler_float("Momento de inercia Iy (flexao, eixo 2) [mm^4]: ")
    Iz = _ler_float("Momento de inercia Iz (flexao, eixo 3) [mm^4]: ")
    J = _ler_float("Constante de torcao J [mm^4]: ")

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": "Valores digitados diretamente"}

def _secao_valores_diretos2(A,Iy,Iz,J) -> dict:
    
    straixyz = ("Digitando A, Iy, Iz e J diretamente (em mm^2 e mm^4).")
    #A = ("Area da secao A [mm^2]: ")
    #Iy = ("Momento de inercia Iy (flexao, eixo 2) [mm^4]: ")
    #Iz = ("Momento de inercia Iz (flexao, eixo 3) [mm^4]: ")
    #J = ("Constante de torcao J [mm^4]: ")

    #A = _ler_float("Area da secao A [mm^2]: ")
    #Iy = _ler_float("Momento de inercia Iy (flexao, eixo 2) [mm^4]: ")
    #Iz = _ler_float("Momento de inercia Iz (flexao, eixo 3) [mm^4]: ")
    #J = _ler_float("Constante de torcao J [mm^4]: ")

    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "descricao": "Valores digitados diretamente"}


def definir_secao() -> dict:
    """
    Menu principal de definicao da secao transversal. Retorna um
    dicionario com as chaves: A, Iy, Iz, J, descricao.
    """
    print()
    print("=== Definicao da secao transversal ===")
    print("1 - Perfil padrão: RETANGULAR (calcula A, Iy, Iz, J automaticamente)")
    print("2 - Perfil padrão: CIRCULAR CHEIO (calcula automaticamente)")
    print("3 - Perfil padrão: CIRCULAR TUBULAR (calcula automaticamente)")
    print('4 - Perfil padrão: Pefil "I" (calcula automaticamente, aproximado)')
    print("5 - Digitar A, Iy, Iz e J diretamente (valores ja calculados)")
    print()

    opcao = input("Escolha uma opcao: ").strip()

    match opcao:
        case "1":
            return _secao_retangular()
        case "2":
            return _secao_circular_cheia()
        case "3":
            return _secao_circular_tubular()
        case "4":
            return _secao_perfil_i()
        case "5":
            return _secao_valores_diretos()
        case _:
            print("Opcao invalida! Tente novamente.")
            return definir_secao()

def definir_secao2() -> dict:
    """
    Menu principal de definicao da secao transversal. Retorna um
    dicionario com as chaves: A, Iy, Iz, J, descricao.
    """
    secstrf1 = (" Definição da seção transversal:\n")
    secstrf2 = ("\n1 - Perfil padrão: retangular (calcula A, Iy, Iz, J automaticamente)")
    secstrf3 = ("\n2 - Perfil padrão: circular compacto (calcula automaticamente)")
    secstrf4 = ("\n3 - Perfil padrão: circular tubular (calcula automaticamente)")
    secstrf5 = ('\n4 - Perfil padrão: Perfil "I" (calcula automaticamente, aproximado)')
    secstrf6 = ("\n5 - Digitar A, Iy, Iz e J diretamente (valores ja calculados)")
    secstrf7 = ("\n\nEscolha uma opcao: ")
    secstrf = secstrf1 + secstrf2 + secstrf3 + secstrf4 + secstrf5 + secstrf6 + secstrf7
    return secstrf
    

    #opcao = input("Escolha uma opcao: ").strip()

    match opcao:
        case "1":
            return _secao_retangular()
        case "2":
            return _secao_circular_cheia()
        case "3":
            return _secao_circular_tubular()
        case "4":
            return _secao_perfil_i()
        case "5":
            return _secao_valores_diretos()
        case _:
            print("Opcao invalida! Tente novamente.")
            return definir_secao()


if __name__ == "__main__":
    resultado = definir_secao()
    print()
    print("=== Secao definida ===")
    print(f"Descricao : {resultado['descricao']}")
    print(f"A         : {resultado['A']:.4f} mm^2")
    print(f"Iy        : {resultado['Iy']:.4f} mm^4")
    print(f"Iz        : {resultado['Iz']:.4f} mm^4")
    print(f"J         : {resultado['J']:.4f} mm^4")
