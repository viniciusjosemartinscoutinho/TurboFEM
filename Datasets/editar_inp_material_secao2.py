# & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\X-tests\editar_inp_material_secao.py #serie 

"""
editar_inp_material_secao.py

Faz uma varredura RECURSIVA a partir da pasta PAI da pasta onde este
script esta, procurando todos os arquivos .inp existentes, e seleciona
automaticamente o MAIS RECENTE (por data de modificacao).

Depois pede ao usuario:
    1) o material (arvore de 2 niveis: categoria -> subtipo especifico,
       com opcao "outro" em qualquer nivel para digitar manualmente)
    2) a secao transversal (perfil padrao calculado, ou valores diretos)

E EDITA o .inp encontrado, inserindo/substituindo os blocos:
    *MATERIAL, *ELASTIC, *DENSITY, *SPECIFIC HEAT, *CONDUCTIVITY,
    *EXPANSION, *BEAM SECTION

Uso:
    python editar_inp_material_secao.py
"""

from pathlib import Path
from datetime import datetime

from selecionar_material import selecionar_material
from secao_transversal import definir_secao


def encontrar_inp_mais_recente(pasta_raiz: Path) -> Path | None:
    """
    Varredura recursiva completa a partir de pasta_raiz, procurando
    todos os arquivos *.inp e retornando o mais recente (maior
    timestamp de modificacao). Retorna None se nao achar nenhum.
    """
    candidatos = list(pasta_raiz.rglob("*.inp"))
    if not candidatos:
        return None

    mais_recente = max(candidatos, key=lambda p: p.stat().st_mtime)
    return mais_recente


def diagnosticar_busca(pasta_raiz: Path, candidatos: list) -> None:
    print(f"[DIAGNOSTICO] Pasta raiz da varredura: {pasta_raiz.resolve()}")
    print(f"[DIAGNOSTICO] Total de arquivos .inp encontrados: {len(candidatos)}")
    for c in sorted(candidatos, key=lambda p: p.stat().st_mtime, reverse=True):
        mtime = datetime.fromtimestamp(c.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"    {mtime}  ->  {c}")
    print()


def montar_bloco_material(nome: str, E: float, nu: float, dens: float,
                            cp: float, k: float, alpha: float) -> list[str]:
    """
    Monta as linhas do bloco *MATERIAL completo no formato do
    CalculiX/Abaqus, incluindo propriedades mecanicas e termicas.
    """
    # Sanitiza o nome para virar um identificador valido de MATERIAL
    # (sem espacos, sem caracteres especiais problematicos).
    nome_id = "".join(c if c.isalnum() else "_" for c in nome).upper()

    linhas = [
        f"*MATERIAL, NAME={nome_id}",
        "*ELASTIC",
        f"{E}, {nu}",
        "*DENSITY",
        f"{dens}",
        "*SPECIFIC HEAT",
        f"{cp}",
        "*CONDUCTIVITY",
        f"{k}",
        "*EXPANSION",
        f"{alpha}",
    ]
    return linhas, nome_id


def montar_bloco_beam_section(nome_material_id: str, elset: str,
                                A: float, Iy: float, Iz: float, J: float) -> list[str]:
    """
    Monta o bloco *BEAM GENERAL SECTION do CalculiX/Abaqus para uma
    barra 1D, referenciando o material e incluindo area + inercias.

    Formato *BEAM GENERAL SECTION:
        linha 1: A, I11, I12, I22, J
        linha 2: vetor n1,n2,n3 (direcao do eixo local 2, perpendicular
                  ao eixo da barra) -- usamos (0,0,1) como padrao (barra
                  ao longo de X, eixo 2 local apontando em Z).
    Aqui I11 = Iz, I22 = Iy, I12 = 0 (produto de inercia nulo, assumindo
    eixos principais de inercia).
    """
    linhas = [
        f"*BEAM GENERAL SECTION, ELSET={elset}, MATERIAL={nome_material_id}, SECTION=GENERAL",
        f"{A}, 0.0, {Iy}, {Iz}",
        f"0.0, 0.0, 1.0",
    ]
    return linhas


def remover_blocos_antigos(linhas_originais: list[str]) -> list[str]:
    """
    Remove do conteudo original do .inp qualquer bloco *MATERIAL ja
    existente (e suas sub-propriedades: *ELASTIC, *DENSITY, etc.) e
    qualquer *SOLID SECTION / *BEAM GENERAL SECTION ja existente, para
    evitar duplicar definicoes quando o script for rodado mais de uma
    vez sobre o mesmo arquivo.
    """
    palavras_chave_bloco_a_remover = (
        "*MATERIAL", "*ELASTIC", "*DENSITY", "*SPECIFIC HEAT",
        "*CONDUCTIVITY", "*EXPANSION", "*SOLID SECTION",
        "*BEAM GENERAL SECTION", "*BEAM SECTION",
    )

    marcador_comentario = "** --- MATERIAL E SECAO INSERIDOS POR EDITAR_INP_MATERIAL_SECAO.PY ---"

    resultado = []
    pulando_linha_de_dados = False

    for linha in linhas_originais:
        linha_upper = linha.strip().upper()

        if linha_upper == marcador_comentario:
            # Remove tambem a linha de comentario marcadora, para nao
            # acumular uma copia dela a cada execucao do script.
            continue

        if linha_upper.startswith(palavras_chave_bloco_a_remover):
            # Esta linha eh uma palavra-chave que queremos remover.
            # A linha de dados imediatamente seguinte (que nao comeca
            # com "*") tambem pertence a este bloco e deve ser pulada.
            pulando_linha_de_dados = True
            continue

        if pulando_linha_de_dados:
            if linha.strip().startswith("*"):
                # Chegou em uma nova palavra-chave -- para de pular,
                # e deixa essa nova linha ser avaliada normalmente
                # (cai para a checagem abaixo).
                pulando_linha_de_dados = False
            else:
                # Ainda eh linha de dados do bloco anterior -- pula.
                continue

        resultado.append(linha)

    return resultado


def editar_inp(caminho_inp: Path, material_tupla: tuple, secao_dict: dict) -> None:
    nome, E, nu, dens, cp, k, alpha = material_tupla

    conteudo_original = caminho_inp.read_text(encoding="utf-8")
    linhas_originais = conteudo_original.splitlines()

    linhas_limpas = remover_blocos_antigos(linhas_originais)

    bloco_material, nome_material_id = montar_bloco_material(nome, E, nu, dens, cp, k, alpha)
    bloco_secao = montar_bloco_beam_section(
        nome_material_id, "BARRA", secao_dict["A"], secao_dict["Iy"],
        secao_dict["Iz"], secao_dict["J"]
    )

    linhas_finais = (
        linhas_limpas
        + ["** --- Material e secao inseridos por editar_inp_material_secao.py ---"]
        + bloco_material
        + bloco_secao
    )

    caminho_inp.write_text("\n".join(linhas_finais) + "\n", encoding="utf-8")


def main_edit_material(cross={"A": 0, "Iy": 0, "Iz": 0, "J": 0, "descricao": "Valores digitados diretamente"},other=0, E=0, nu=0, ro=0, cp=0, kmaterial=0, alpha=0):
    script_dir = Path(__file__).resolve().parent
    pasta_pai = script_dir.parent

    print(f"[DIAGNOSTICO] Pasta do script: {script_dir}")
    print(f"[DIAGNOSTICO] Pasta pai (raiz da varredura): {pasta_pai}")
    print()

    candidatos = list(pasta_pai.rglob("*.inp"))
    diagnosticar_busca(pasta_pai, candidatos)

    inp_mais_recente = encontrar_inp_mais_recente(pasta_pai)

    if inp_mais_recente is None:
        print("ERRO: nenhum arquivo .inp foi encontrado na varredura recursiva")
        print(f"a partir de: {pasta_pai}")
        print("Gere um .inp primeiro (ex: geometria_barra_1d_param.py) e tente de novo.")
        return

    print(f"OK: .inp mais recente selecionado -> {inp_mais_recente}")
    print()

    print("Agora escolha o material da barra.")
    material_tupla = selecionar_material()
    propmat2 = E*nu*ro*cp*kmaterial*alpha                                    
    #other, E, nu, ro, cp, kmaterial, alpha                                    

    print()
    print("Agora defina a secao transversal da barra.")
    secao_dict = definir_secao()
    cross2D = secao_dict
    A2 = cross['A']
    Iy2 = cross['Iy']
    Iz2 = cross['Iz']
    J2 = cross['J']
    if((A2*Iy2*Iz2*J2) == 0):
        secao_dict = cross2D
    else:
        secao_dict = cross 

    print()
    print("=== Resumo antes de editar o arquivo ===")
    if(propmat2 == 0):
        nome, E, nu, dens, cp, k, alpha = material_tupla 
    else:
        nome = other
        E = E
        nu = nu
        dens = ro
        cp = cp
        k = kmaterial
        alpha = alpha
    print(f"Material : {nome}")
    material_tupla = [nome, E, nu, dens, cp, k, alpha]
    

    print(f"  E={E} MPa | nu={nu} | dens={dens} ton/mm^3")
    print(f"  cp={cp} mJ/(ton.K) | k={k} mW/(mm.K) | alpha={alpha} 1/K")
    print(f"Secao    : {secao_dict['descricao']}")
    print(f"  A={secao_dict['A']:.4f} mm^2 | Iy={secao_dict['Iy']:.4f} mm^4 "
          f"| Iz={secao_dict['Iz']:.4f} mm^4 | J={secao_dict['J']:.4f} mm^4")
    print()

    #confirmacao = input(f"Confirmar edicao de '{inp_mais_recente.name}'? (s/n): ").strip().lower()
    if False:
        #confirmacao != "s":
        print("Operacao cancelada pelo usuario. Nenhum arquivo foi alterado.")
        return

    editar_inp(inp_mais_recente, material_tupla, secao_dict)
    print()
    print(f"OK: arquivo editado com sucesso -> {inp_mais_recente}")


if __name__ == "__main__":
    main_edit_material()
