import os
from pathlib import Path
import re
import threading
import traceback
from collections import Counter

# --- Forçar pasta de pacotes dentro do diretório do script ---
# ATENÇÃO: a variável correta é ARGOS_PACKAGES_DIR (sem "TRANSLATE" no meio).
SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGES_DIR = SCRIPT_DIR / "argos_packages"
PACKAGES_DIR.mkdir(exist_ok=True)
os.environ["ARGOS_PACKAGES_DIR"] = str(PACKAGES_DIR)

MARCADOR_SETUP = PACKAGES_DIR / ".setup_completo"

import argostranslate.package
import argostranslate.translate
import langdetect
import stanza

# --- Forçar o stanza a nunca tentar acessar a internet ---
# O argostranslate (em argostranslate/sbd.py) cria internamente um
# stanza.Pipeline(...) para dividir o texto em frases antes de traduzir, SEM
# especificar download_method. O padrão do stanza nesse caso é
# DOWNLOAD_RESOURCES, que sempre tenta buscar o índice de versões em
# raw.githubusercontent.com antes de usar os modelos já instalados
# localmente -- isso é independente do MARCADOR_SETUP acima (que só controla
# o download dos pacotes do próprio argostranslate). Sem internet, essa
# checagem trava/expira em timeout e o erro sobe disfarçado como
# "attempted relative import with no known parent package" no seu except.
#
# Aqui a gente troca o stanza.Pipeline por uma versão que sempre força
# download_method=NONE quando quem chamou não especificou nada -- assim ele
# usa só o que já está no disco e nunca sai pedindo nada pela rede. Como é o
# mesmo objeto de módulo em memória, isso vale também para a chamada
# interna que o argostranslate faz, mesmo sem editar o código dele.
_stanza_pipeline_original = stanza.Pipeline


def _stanza_pipeline_offline(*args, **kwargs):
    kwargs.setdefault("download_method", stanza.DownloadMethod.NONE)
    return _stanza_pipeline_original(*args, **kwargs)


stanza.Pipeline = _stanza_pipeline_offline

# argostranslate/langdetect não são garantidamente thread-safe para chamadas
# concorrentes de duas threads diferentes usando o mesmo modelo carregado.
# Esse lock serializa qualquer chamada real de tradução, mesmo se motor_tradutor
# for chamado de várias threads ao mesmo tempo (ex: várias TradutorWorker rodando
# em paralelo numa interface gráfica).
_traducao_lock = threading.Lock()

IDIOMAS = {
    "português": "pt", "english": "en", "français": "fr", "deutsch": "de",
    "español": "es", "italiano": "it", "nederlands": "nl", "dansk": "da",
    "svenska": "sv", "norsk": "no", "suomi": "fi", "日本語": "ja",
    "한국어": "ko", "中文": "zh", "русский": "ru", "العربية": "ar",
}

def nome_para_codigo(nome):
    return IDIOMAS.get(nome)


def _tem_repeticao_suspeita(texto, limite_repeticoes=4):
    """
    Detecta degeneração típica de modelos de tradução neural em textos curtos/ambíguos:
    o decodificador entra em loop e repete a mesma palavra ou substring várias vezes
    (ex: "mainmainmainmain..." ou "main main main main"). Se detectar isso, a
    tradução deve ser descartada.
    """
    if not texto:
        return False

    # substring curta (2 a 12 caracteres) repetida 4+ vezes seguidas, com ou sem espaço
    if re.search(r"(.{2,12}?)\1{" + str(limite_repeticoes - 1) + r",}", texto):
        return True

    palavras = re.findall(r"\w+", texto.lower())
    if len(palavras) >= limite_repeticoes:
        maior_sequencia = 1
        sequencia_atual = 1
        for i in range(1, len(palavras)):
            if palavras[i] == palavras[i - 1]:
                sequencia_atual += 1
                maior_sequencia = max(maior_sequencia, sequencia_atual)
            else:
                sequencia_atual = 1
        if maior_sequencia >= limite_repeticoes:
            return True

        contagem = Counter(palavras)
        _, qtd = contagem.most_common(1)[0]
        if len(palavras) >= 6 and qtd / len(palavras) >= 0.5:
            return True

    return False


def _diagnostico_pacotes():
    """
    DIAGNÓSTICO TEMPORÁRIO — chamado sempre no início de motor_tradutor() enquanto
    estivermos caçando o bug de "só pt/en carregam dentro do .exe". Imprime tudo
    que precisamos saber sobre o estado real do argostranslate em runtime.
    Remover (ou só deixar de chamar) depois que o problema for resolvido.
    """
    print(f"[DIAG] ARGOS_PACKAGES_DIR (env) = {os.environ.get('ARGOS_PACKAGES_DIR')}")
    print(f"[DIAG] PACKAGES_DIR (calculado) = {PACKAGES_DIR}")
    print(f"[DIAG] PACKAGES_DIR existe?     = {PACKAGES_DIR.exists()}")

    try:
        import argostranslate.settings as _settings
        print(f"[DIAG] argostranslate.settings.package_data_dir = {getattr(_settings, 'package_data_dir', '???')}")
        print(f"[DIAG] argostranslate.settings.data_dir         = {getattr(_settings, 'data_dir', '???')}")
    except Exception as e:
        print(f"[DIAG] não consegui ler argostranslate.settings: {e}")

    if PACKAGES_DIR.exists():
        subpastas = sorted(p.name for p in PACKAGES_DIR.iterdir() if p.is_dir())
        print(f"[DIAG] Subpastas dentro de PACKAGES_DIR ({len(subpastas)}): {subpastas}")
    else:
        print("[DIAG] PACKAGES_DIR NÃO EXISTE NO DISCO -- isso já seria a causa raiz.")

    print(f"[DIAG] MARCADOR_SETUP ({MARCADOR_SETUP}) existe? = {MARCADOR_SETUP.exists()}")

    try:
        idiomas_instalados = argostranslate.translate.get_installed_languages()
        codigos = [l.code for l in idiomas_instalados]
        print(f"[DIAG] Idiomas que o argostranslate.translate.get_installed_languages() enxerga ({len(codigos)}): {codigos}")
    except Exception as e:
        print(f"[DIAG] erro ao chamar get_installed_languages(): {e}")

    try:
        instalados_pkg = argostranslate.package.get_installed_packages()
        pares = [(p.from_code, p.to_code) for p in instalados_pkg]
        print(f"[DIAG] Pacotes que argostranslate.package.get_installed_packages() enxerga ({len(pares)}): {pares}")
    except Exception as e:
        print(f"[DIAG] erro ao chamar get_installed_packages(): {e}")


def _baixar_todos_modelos():
    """
    Roda só uma vez de fato: baixa TODOS os pares idioma<->en do dicionário
    direto para PACKAGES_DIR (pasta do script). Depois cria um arquivo
    marcador pra nunca mais tentar checar/baixar nada nas próximas execuções.
    """
    if MARCADOR_SETUP.exists():
        print("[setup] MARCADOR_SETUP já existe -> pulando qualquer instalação/checagem.")
        return

    print("[setup] Primeira execução: baixando todos os modelos de tradução...")
    argostranslate.package.update_package_index()
    disponiveis = argostranslate.package.get_available_packages()
    instalados = argostranslate.package.get_installed_packages()
    pares_instalados = {(p.from_code, p.to_code) for p in instalados}

    codigos = set(IDIOMAS.values())
    for cod in codigos:
        if cod == "en":
            continue
        for par in [(cod, "en"), ("en", cod)]:
            if par in pares_instalados:
                continue
            pacote = next(
                (p for p in disponiveis if p.from_code == par[0] and p.to_code == par[1]),
                None,
            )
            if pacote:
                try:
                    caminho_baixado = pacote.download()
                    argostranslate.package.install_from_path(caminho_baixado)
                    print(f"[setup] instalado {par[0]} -> {par[1]}")
                except Exception as e:
                    print(f"[aviso] falha ao instalar {par}: {e}")
            else:
                print(f"[aviso] pacote {par} não encontrado no índice do Argos")

    MARCADOR_SETUP.touch()
    print("[setup] concluído. Pasta usada:", PACKAGES_DIR)


def motor_tradutor00(texto, language, idioma_origem=None, debug=False):
    """
    Traduz `texto` para `language` (nome do idioma, chave do dicionário IDIOMAS),
    usando inglês como pivô.

    idioma_origem: opcional. Se você já SABE em que idioma o texto foi escrito
        (ex: você mesmo escreveu a pergunta em português), passe o nome dele
        aqui (ex: "português"). Isso evita depender do langdetect, que erra
        com frequência em frases curtas tipo "quantos elementos?".
        Se None (padrão), tenta detectar automaticamente.

    debug: se True, imprime no terminal o idioma detectado/usado e se alguma
        proteção (idioma não suportado, detecção falhou, tradução degenerada)
        foi acionada — útil pra descobrir POR QUE uma tradução não aconteceu,
        em vez de só receber o texto original de volta silenciosamente.

    Se qualquer etapa falhar (idioma não detectável, código não suportado,
    modelo ausente, tradução degenerada/repetitiva, etc.), retorna o texto
    original SEM traduzir.
    """
    def _log(msg):
        if debug:
            print(f"[motor_tradutor] {msg}")

    try:
        with _traducao_lock:
            _baixar_todos_modelos()

            destino_cod = nome_para_codigo(language)
            if destino_cod is None:
                _log(f"idioma de destino '{language}' não está no dicionário IDIOMAS -> mantendo original")
                return texto

            if idioma_origem is not None:
                origem_cod = nome_para_codigo(idioma_origem)
                if origem_cod is None:
                    _log(f"idioma_origem '{idioma_origem}' não está no dicionário IDIOMAS -> mantendo original")
                    return texto
            else:
                try:
                    origem_cod = langdetect.detect(texto)
                    _log(f"idioma de origem detectado automaticamente: '{origem_cod}' (para o texto: {texto!r})")
                except Exception as e:
                    _log(f"langdetect falhou ({e}) -> mantendo original")
                    return texto

            idiomas_instalados = argostranslate.translate.get_installed_languages()
            lang_origem = next((l for l in idiomas_instalados if l.code == origem_cod), None)
            lang_en = next((l for l in idiomas_instalados if l.code == "en"), None)
            lang_destino = next((l for l in idiomas_instalados if l.code == destino_cod), None)

            if lang_en is None or lang_destino is None or lang_origem is None:
                _log(f"modelo ausente (origem={origem_cod}, en={lang_en is not None}, destino={destino_cod}) -> mantendo original")
                return texto

            if origem_cod == destino_cod:
                return texto

            if origem_cod == "en":
                texto_en = texto
            else:
                trad_para_en = lang_origem.get_translation(lang_en)
                if trad_para_en is None:
                    _log(f"sem modelo {origem_cod}->en -> mantendo original")
                    return texto
                texto_en = trad_para_en.translate(texto)

            if destino_cod == "en":
                resultado = texto_en
            else:
                trad_final = lang_en.get_translation(lang_destino)
                if trad_final is None:
                    _log(f"sem modelo en->{destino_cod} -> devolvendo versão em inglês")
                    return texto_en
                resultado = trad_final.translate(texto_en)

            if _tem_repeticao_suspeita(resultado):
                _log(f"tradução degenerada/repetitiva detectada ({resultado!r}) -> mantendo original")
                return texto

            return resultado

    except Exception as e:
        # DIAGNÓSTICO TEMPORÁRIO: imprime o traceback completo (não só a mensagem)
        # para localizar exatamente o arquivo/linha onde o import relativo quebra
        # dentro do .exe empacotado. Reverter para o log simples depois de resolver.
        if debug:
            print(f"[motor_tradutor] erro inesperado ({e}) -> mantendo original")
            traceback.print_exc()
        else:
            _log(f"erro inesperado ({e}) -> mantendo original")
        return texto

def motor_tradutor(texto, language, idioma_origem=None, debug=True):
    """
    Traduz `texto` para `language` (nome do idioma, chave do dicionário IDIOMAS),
    usando inglês como pivô.

    idioma_origem: opcional. Se você já SABE em que idioma o texto foi escrito
        (ex: você mesmo escreveu a pergunta em português), passe o nome dele
        aqui (ex: "português"). Isso evita depender do langdetect, que erra
        com frequência em frases curtas tipo "quantos elementos?".
        Se None (padrão), tenta detectar automaticamente.

    debug: se True, imprime no terminal o idioma detectado/usado e se alguma
        proteção (idioma não suportado, detecção falhou, tradução degenerada)
        foi acionada — útil pra descobrir POR QUE uma tradução não aconteceu,
        em vez de só receber o texto original de volta silenciosamente.

        *** TEMPORARIAMENTE FORÇADO PARA True POR PADRÃO *** enquanto
        investigamos por que só pt/en carregam dentro do .exe empacotado.
        Depois de resolver, volte o default pra False.

    Se qualquer etapa falhar (idioma não detectável, código não suportado,
    modelo ausente, tradução degenerada/repetitiva, etc.), retorna o texto
    original SEM traduzir.
    """
    def _log(msg):
        if debug:
            print(f"[motor_tradutor] {msg}")

    try:
        with _traducao_lock:
            # DIAGNÓSTICO TEMPORÁRIO -- roda toda vez, no início, antes de qualquer outra coisa.
            if debug:
                _diagnostico_pacotes()

            _baixar_todos_modelos()

            destino_cod = nome_para_codigo(language)
            if destino_cod is None:
                _log(f"idioma de destino '{language}' não está no dicionário IDIOMAS -> mantendo original")
                return texto

            if idioma_origem is not None:
                origem_cod = nome_para_codigo(idioma_origem)
                if origem_cod is None:
                    _log(f"idioma_origem '{idioma_origem}' não está no dicionário IDIOMAS -> mantendo original")
                    return texto
            else:
                try:
                    origem_cod = langdetect.detect(texto)
                    _log(f"idioma de origem detectado automaticamente: '{origem_cod}' (para o texto: {texto!r})")
                except Exception as e:
                    _log(f"langdetect falhou ({e}) -> mantendo original")
                    return texto

            idiomas_instalados = argostranslate.translate.get_installed_languages()
            lang_origem = next((l for l in idiomas_instalados if l.code == origem_cod), None)
            lang_en = next((l for l in idiomas_instalados if l.code == "en"), None)
            lang_destino = next((l for l in idiomas_instalados if l.code == destino_cod), None)

            if lang_en is None or lang_destino is None or lang_origem is None:
                _log(f"modelo ausente (origem={origem_cod} -> {'OK' if lang_origem else 'FALTANDO'}, "
                     f"en -> {'OK' if lang_en else 'FALTANDO'}, "
                     f"destino={destino_cod} -> {'OK' if lang_destino else 'FALTANDO'}) -> mantendo original")
                return texto

            if origem_cod == destino_cod:
                return texto

            if origem_cod == "en":
                texto_en = texto
            else:
                trad_para_en = lang_origem.get_translation(lang_en)
                if trad_para_en is None:
                    _log(f"sem modelo {origem_cod}->en -> mantendo original")
                    return texto
                texto_en = trad_para_en.translate(texto)

            if destino_cod == "en":
                resultado = texto_en
            else:
                trad_final = lang_en.get_translation(lang_destino)
                if trad_final is None:
                    _log(f"sem modelo en->{destino_cod} -> devolvendo versão em inglês")
                    return texto_en
                resultado = trad_final.translate(texto_en)

            if _tem_repeticao_suspeita(resultado):
                _log(f"tradução degenerada/repetitiva detectada ({resultado!r}) -> mantendo original")
                return texto

            return resultado

    except Exception as e:
        # DIAGNÓSTICO TEMPORÁRIO: imprime o traceback completo (não só a mensagem)
        # para localizar exatamente o arquivo/linha onde o import relativo quebra
        # dentro do .exe empacotado. Reverter para o log simples depois de resolver.
        if debug:
            print(f"[motor_tradutor] erro inesperado ({e}) -> mantendo original")
            traceback.print_exc()
        else:
            _log(f"erro inesperado ({e}) -> mantendo original")
        return texto


def test_language(language: str) -> bool:
    """Retorna True se `language` for uma chave válida do dicionário IDIOMAS."""
    return language in IDIOMAS


if __name__ == "__main__":
    import argostranslate.settings as _s
    print("Pasta de pacotes em uso:", _s.package_data_dir)

    print(motor_tradutor("日本", "français", debug=True))
    print(motor_tradutor("𓀀𓂀𓃀", "português", debug=True))  # hieróglifo -> mantém original
    print(motor_tradutor("quantos elementos?", "français", idioma_origem="português", debug=True))