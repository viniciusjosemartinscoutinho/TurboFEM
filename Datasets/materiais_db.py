"""
materiais_db.py

Banco de dados de materiais mais usados na industria mecanica/FEM na
Franca e Alemanha (automotivo, aeroespacial, nuclear, maquinario).

Valores de referencia: Callister "Materials Science and Engineering",
ASM Metals Handbook, MatWeb, normas DIN/EN/AFNOR. Sao valores TIPICOS
de literatura -- para projeto critico, sempre confirmar com a ficha
tecnica (datasheet) do fornecedor/norma especifica do lote.

Unidades usadas neste banco (compativeis com .inp do CalculiX em mm):
    E      -> MPa   (N/mm^2)
    nu     -> adimensional
    dens   -> ton/mm^3   (para manter consistencia com E em MPa e
                           comprimentos em mm -- ver nota de unidades
                           no script principal)
    cp     -> mJ/(ton.K)  (calor especifico, na mesma familia de unidades)
    k      -> mW/(mm.K)   (condutividade termica)
    alpha  -> 1/K          (coeficiente de dilatacao linear)

Estrutura em arvore de 2 niveis:
    NIVEL 1 (categoria) -> alguns materiais sao "simples" (1 unico jogo
    de propriedades, ex: cobre, latao, vidro). Outros sao "compostos"
    (aco, ferro fundido, titanio) e exigem um NIVEL 2 (subtipo
    especifico), porque as propriedades mudam MUITO dentro da mesma
    familia.
"""

# Materiais "simples": 1 categoria = 1 jogo de propriedades direto.
# Cada entrada: (nome_exibicao, E[MPa], nu, dens[ton/mm3], cp[mJ/(ton.K)], k[mW/(mm.K)], alpha[1/K])
MATERIAIS_SIMPLES = {
    "aluminio_6061":   ("Aluminio 6061-T6",        69000.0, 0.33, 2.70e-9, 8.96e8, 167.0, 23.6e-6),
    "aluminio_7075":   ("Aluminio 7075-T6",        71700.0, 0.33, 2.81e-9, 9.60e8, 130.0, 23.6e-6),
    "aluminio_2024":   ("Aluminio 2024-T3",        73100.0, 0.33, 2.78e-9, 8.75e8, 121.0, 23.2e-6),
    "titanio_ti6al4v": ("Titanio Ti-6Al-4V",      113800.0, 0.34, 4.43e-9, 5.26e8,   6.7, 8.6e-6),
    "cobre":           ("Cobre puro (C11000)",    117000.0, 0.34, 8.96e-9, 3.85e8, 401.0, 16.5e-6),
    "latao":           ("Latao (CuZn37)",         100000.0, 0.34, 8.50e-9, 3.80e8, 120.0, 20.0e-6),
    "bronze":          ("Bronze (CuSn8)",         110000.0, 0.34, 8.80e-9, 3.77e8,  50.0, 18.0e-6),
    "magnésio_az31":   (" magnésio (AZ31B)",          45000.0, 0.35, 1.77e-9, 1.02e9,  96.0, 26.0e-6),
    "niquel_inconel":  ("Inconel 625 (liga Ni)",  207000.0, 0.31, 8.44e-9, 4.10e8,   9.8, 12.8e-6),
    "ferro_fundido_nodular": ("Ferro fundido nodular (GGG40)", 169000.0, 0.275, 7.10e-9, 4.60e8, 36.0, 11.5e-6),
    "policarbonato":   ("Policarbonato (PC)",       2400.0, 0.37, 1.20e-9, 1.20e9,   0.20, 65.0e-6),
    "pa6_nylon":       ("Poliamida PA6 (Nylon)",    2800.0, 0.39, 1.14e-9, 1.70e9,   0.25, 80.0e-6),
    "concreto":        ("Concreto estrutural C30",  30000.0, 0.20, 2.40e-9, 8.80e8,   1.70, 10.0e-6),
    "vidro":           ("Vidro (silicato comum)",   70000.0, 0.22, 2.50e-9, 8.40e8,   1.00, 9.0e-6),
    "fibra_carbono_unidir": ("Fibra de carbono unidirecional (CFRP)", 135000.0, 0.30, 1.60e-9, 9.00e8, 7.0, 2.0e-6),
}

# Materiais "compostos": tem grande variacao interna, entao a categoria
# de NIVEL 1 so existe para agrupar visualmente -- a escolha real de
# propriedades vem do NIVEL 2 (subtipo).
#
# Estrutura: { "categoria": { "subtipo_key": (nome, E, nu, dens, cp, k, alpha) } }
MATERIAIS_COMPOSTOS = {
    "Aco": {
        "aco_1020":     ("Aco carbono SAE/AISI 1020",     205000.0, 0.29, 7.87e-9, 4.86e8, 51.9, 11.7e-6),
        "aco_1045":     ("Aco carbono SAE/AISI 1045",     200000.0, 0.29, 7.85e-9, 4.86e8, 49.8, 11.6e-6),
        "aco_4140":     ("Aco liga SAE/AISI 4140 (Cr-Mo)", 205000.0, 0.29, 7.85e-9, 4.73e8, 42.6, 12.3e-6),
        "aco_316":      ("Aco inox AISI 316",              193000.0, 0.27, 8.00e-9, 5.00e8, 16.2, 16.0e-6),
        "aco_304":      ("Aco inox AISI 304",              193000.0, 0.27, 7.90e-9, 5.00e8, 16.2, 17.0e-6),
        "aco_s355":     ("Aco estrutural S355 (EN 10025)", 210000.0, 0.30, 7.85e-9, 4.86e8, 50.0, 12.0e-6),
        "aco_e335":     ("Aco mecanico Ck45 / E335 (DIN)", 210000.0, 0.30, 7.85e-9, 4.86e8, 47.0, 12.0e-6),
        "aco_maraging": ("Aco maraging 18Ni (alta resist.)", 190000.0, 0.30, 8.10e-9, 4.60e8, 25.0, 10.1e-6),
    },
    "ferro_fundido": {
        "ferro_cinzento":  ("Ferro fundido cinzento (GG25 / EN-GJL-250)", 110000.0, 0.26, 7.20e-9, 4.60e8, 50.0, 10.5e-6),
        "ferro_branco":    ("Ferro fundido branco",                       170000.0, 0.27, 7.70e-9, 4.50e8, 28.0, 10.0e-6),
        "ferro_nodular_60": ("Ferro fundido nodular GGG60 (EN-GJS-600)",   175000.0, 0.275, 7.10e-9, 4.60e8, 32.0, 11.5e-6),
        "ferro_maleavel":  ("Ferro fundido maleavel",                     170000.0, 0.27, 7.30e-9, 4.60e8, 45.0, 11.0e-6),
    },
    "titanio": {
        "ti_grau2":   ("Titanio Grau 2 (puro comercial)", 103000.0, 0.34, 4.51e-9, 5.23e8, 16.4, 8.6e-6),
        "ti_6al4v":   ("Titanio Ti-6Al-4V (Grau 5)",      113800.0, 0.34, 4.43e-9, 5.26e8,  6.7, 8.6e-6),
        "ti_beta21s": ("Titanio Beta 21S (alta resist.)", 100000.0, 0.33, 4.94e-9, 5.10e8,  7.8, 8.0e-6),
    },
    "aluminio_estrutural": {
        "al_6061": ("Aluminio 6061-T6",   69000.0, 0.33, 2.70e-9, 8.96e8, 167.0, 23.6e-6),
        "al_7075": ("Aluminio 7075-T6",   71700.0, 0.33, 2.81e-9, 9.60e8, 130.0, 23.6e-6),
        "al_2024": ("Aluminio 2024-T3",   73100.0, 0.33, 2.78e-9, 8.75e8, 121.0, 23.2e-6),
        "al_5083": ("Aluminio 5083 (naval/offshore)", 70300.0, 0.33, 2.66e-9, 9.00e8, 117.0, 23.8e-6),
    },
}

# Lista ordenada de categorias para exibir no menu principal (nivel 1).
# "tipo": "simples" -> usa direto MATERIAIS_SIMPLES[key]
# "tipo": "composto" -> precisa abrir o submenu em MATERIAIS_COMPOSTOS[key]
MENU_NIVEL_1 = [
    ("aco",                 "Aço (varia MUITO -> sub-menu)",              "composto"),
    ("ferro fundido",       "Ferro fundido (varia MUITO -> sub-menu)",    "composto"),
    ("titanio",             "Titânio (varia -> sub-menu)",                "composto"),
    ("aluminio_estrutural", "Aluminio estrutural (varia -> sub-menu)",    "composto"),
    ("cobre",               "Cobre puro",                                  "simples"),
    ("latao",                "Latao",                                       "simples"),
    ("bronze",               "Bronze",                                      "simples"),
    ("magnesio_az31",        " magnésio (AZ31B) ",                              "simples"),
    ("niquel_inconel",       "Inconel 625 (liga de niquel)",                "simples"),
    ("ferro_fundido_nodular","Ferro fundido nodular GGG40 (valor unico)",   "simples"),
    ("policarbonato",        "Policarbonato (PC)",                          "simples"),
    ("pa6_nylon",            "Poliamida PA6 (Nylon)",                       "simples"),
    ("concreto",             "Concreto estrutural C30",                     "simples"),
    ("vidro",                "Vidro (silicato comum)",                      "simples"),
    ("fibra_carbono_unidir", "Fibra de carbono unidirecional (CFRP)",       "simples"),
]
