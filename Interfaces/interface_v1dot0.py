# & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V\inteface-v1.py
import sys
import math
import queue
import shutil
import subprocess
from pathlib import Path
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QRegularExpression,
    QEventLoop,
    QTimer,
    QSize,
)
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QIcon,
    QRegularExpressionValidator,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QFileDialog,
    QDialog,
    QGridLayout,
)
from motor_tradutor import motor_tradutor
from selecionar_material2 import (
    selecionar_material2,
    selecionar_material3,
    selecionar_material3b,
)
from materiais_db2 import (
    MATERIAIS_SIMPLES,
    MATERIAIS_COMPOSTOS,
    MENU_NIVEL_1,
)
from secao_transversal2 import (
    definir_secao2,
    _secao_retangular2,
    _secao_circular_cheia2,
    _secao_circular_tubular2,
    _secao_perfil_i2,
    _secao_valores_diretos2,
)

#run code.py
def run_my_python_in_serie(script, *args):
    """
    Executa um script Python que está na mesma pasta deste arquivo.

    Exemplo:
        run_my_python("teste.py")
        run_my_python("teste.py", "arg1", "arg2")
    """
    pasta = Path(__file__).parent
    caminho_script = pasta / script

    subprocess.run(
        [sys.executable, str(caminho_script), *map(str, args)],
        check=True
    )

def parallelism_of_run_my_python(script, *args):
    pasta = Path(__file__).parent
    caminho_script = pasta / script

    return subprocess.Popen(
        [sys.executable, str(caminho_script), *map(str, args)]
    )

SCRIPT_DIR = Path(__file__).resolve().parent
LOGO_PATH = SCRIPT_DIR / "Fast-FEA-Logo.png"

#functions that copy and change the scripts...
def copy_and_change_script(nome_script, linha, nova_linha):
    """
    nome_script : str
        Nome do arquivo a procurar (ex.: 'teste.py')

    linha : int
        Número da linha (começando em 1)

    nova_linha : str
        Conteúdo que substituirá a linha

    Retorna:
        str -> caminho completo do novo arquivo
    """

    pasta_script = Path(__file__).parent

    # Procura recursivamente o arquivo
    arquivo_original = None
    for arq in pasta_script.rglob(nome_script):
        arquivo_original = arq
        break

    if arquivo_original is None:
        raise FileNotFoundError(f"Arquivo '{nome_script}' não encontrado.")

    # Nome da cópia
    arquivo_copia = pasta_script / (
        arquivo_original.stem + "_copy" + arquivo_original.suffix
    )

    # Copia o arquivo
    shutil.copy2(arquivo_original, arquivo_copia)

    # Lê todas as linhas
    linhas = arquivo_copia.read_text(encoding="utf-8").splitlines()

    if linha < 1 or linha > len(linhas):
        raise IndexError(
            f"O arquivo possui apenas {len(linhas)} linhas."
        )

    # Substitui a linha
    linhas[linha - 1] = nova_linha

    # Salva novamente
    arquivo_copia.write_text(
        "\n".join(linhas) + "\n",
        encoding="utf-8"
    )

    return str(arquivo_copia)

def try_copy_and_change_script(nome_script, linha, nova_linha):
    try:
        #only try...
        return copy_and_change_script(nome_script, linha, nova_linha)
    except Exception as e:
        print(f"Erro: {e}")
        return None

def copy_and_change_script2(nome_script, alteracoes):
    """
    nome_script : str
        Nome do arquivo a procurar

    alteracoes : list[tuple]
        Lista de (linha_antiga, linha_nova)

    Retorna:
        str -> caminho completo do novo arquivo copiado
    """

    pasta_script = Path(__file__).parent

    # Procura recursivamente o arquivo
    arquivo_original = None
    for arq in pasta_script.rglob(nome_script):
        arquivo_original = arq
        break

    if arquivo_original is None:
        raise FileNotFoundError(f"Arquivo '{nome_script}' não encontrado.")

    # Cria cópia
    arquivo_copia = pasta_script / (
        arquivo_original.stem + "_copy" + arquivo_original.suffix
    )

    shutil.copy2(arquivo_original, arquivo_copia)

    # Lê linhas
    linhas = arquivo_copia.read_text(encoding="utf-8").splitlines()

    # Faz todas as substituições
    for linha_antiga, linha_nova in alteracoes:

        encontrou = False

        for i, conteudo in enumerate(linhas):
            if conteudo == linha_antiga:
                linhas[i] = linha_nova
                encontrou = True
                break

        if not encontrou:
            raise ValueError(f"Linha não encontrada: {linha_antiga}")

    # Salva
    arquivo_copia.write_text(
        "\n".join(linhas) + "\n",
        encoding="utf-8"
    )

    return str(arquivo_copia)

def try_copy_and_change_script2(script, list_of_chages_A2B):
    try:
        #only try...
        return copy_and_change_script2(script, list_of_chages_A2B)
    except Exception as e:
        print(f"Erro: {e}")
        return None

def try_copy_and_change_script(nome_script, linha, nova_linha):
    try:
        #only try...
        return copy_and_change_script(nome_script, linha, nova_linha)
    except Exception as e:
        print(f"Erro: {e}")
        return None

#example
#script = "testgeo2.py"
#alteracoes = [("L  = 150", "L = 200"),("N_NODES = 15", f"N_NODES = {N_e}")]
#novo_script = copy_and_change_script(script, alteracoes)
#print(novo_script)


# functions that just read txt about language...
def speakit(txt: Path) -> str:
    txt = Path(txt)
    return txt.read_text(encoding="utf-8")

def readkeys() -> str:
    # pasta onde está o script
    pasta_script = Path(__file__).parent

    # caminho do keys.txt
    arquivo = pasta_script / "keys.txt"

    # retorna todo o conteúdo do arquivo como uma string
    return arquivo.read_text(encoding="utf-8")

def save_key(string: str, txt) -> None:
    Path(txt).write_text(string, encoding="utf-8")

def test_language(language: str) -> bool:
    """
    Retorna True se `language` for um dos idiomas aceitos (chave do dicionário IDIOMAS),
    False caso contrário.
    """
    return language in IDIOMAS

#new class
class FilaTradutorWorker(QThread):
    """
    UMA ÚNICA thread persistente que processa as traduções em fila, uma de
    cada vez, na ordem em que foram pedidas. Evita rodar várias traduções
    concorrentes (que causavam resultados inconsistentes/aleatórios, já que
    argostranslate/langdetect não são garantidamente thread-safe para chamadas
    simultâneas de threads diferentes).
    """
    pronto = Signal(object, str)  # (alvo, texto_traduzido) — alvo pode ser um QLabel OU um dict {"tipo": "imagem", "indice": N}

    def __init__(self):
        super().__init__()
        self._fila = queue.Queue()
        self._rodando = True

    def enfileirar(self, texto_original, idioma_destino, alvo, idioma_origem=None):
        self._fila.put((texto_original, idioma_destino, alvo, idioma_origem))

    def parar(self):
        self._rodando = False
        self._fila.put(None)  # sentinela pra destravar o queue.get() bloqueado

    def run(self):
        while self._rodando:
            item = self._fila.get()
            if item is None:
                break
            texto_original, idioma_destino, alvo, idioma_origem = item
            traduzido = motor_tradutor(texto_original, idioma_destino, idioma_origem=idioma_origem)
            self.pronto.emit(alvo, traduzido)

class _ImagemComZoom(QLabel):
    """
    QLabel especializada só pra poder capturar o evento de scroll do mouse
    (wheelEvent) e usar isso pra dar zoom na imagem, em vez do comportamento
    padrão de rolar a tela.
    """

    def __init__(self, callback_zoom):
        super().__init__()
        self._callback_zoom = callback_zoom

    def wheelEvent(self, event):
        self._callback_zoom(event.angleDelta().y())
        event.accept()

class _DialogoEscolherExtensao(QDialog):
    """
    Diálogo simples de seleção: mostra a pergunta (já traduzida) e um botão
    pra cada extensão de arquivo. Clicar num botão fecha o diálogo e guarda
    a extensão escolhida em self.extensao_escolhida.
    """

    def __init__(self, pergunta_texto, extensoes, parent=None):
        super().__init__(parent)
        self.extensao_escolhida = None

        self.setWindowTitle("Selecionar tipo de arquivo")
        self.setStyleSheet("background-color: #1c1c24;")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        label = QLabel(pergunta_texto)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 600;")
        layout.addWidget(label)

        grade = QGridLayout()
        grade.setSpacing(10)
        colunas = 4
        for i, ext in enumerate(extensoes):
            botao = QPushButton(ext)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setMinimumHeight(40)
            botao.setStyleSheet("""
                QPushButton {
                    background-color: rgba(148, 92, 255, 160);
                    border: 1.5px solid rgba(148, 92, 255, 220);
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(148, 92, 255, 210);
                }
            """)
            botao.clicked.connect(lambda _checked=False, e=ext: self._escolher(e))
            grade.addWidget(botao, i // colunas, i % colunas)
        layout.addLayout(grade)

        cancelar = QPushButton("Cancelar")
        cancelar.setCursor(Qt.PointingHandCursor)
        cancelar.setStyleSheet("color: rgba(255,255,255,160); background: transparent; border: none;")
        cancelar.clicked.connect(self.reject)
        layout.addWidget(cancelar)

    def _escolher(self, extensao):
        self.extensao_escolhida = extensao
        self.accept()

#inteface's class to download
class JanelaSecundaria(QWidget):
    """
    Uso:
        ja2 = JanelaSecundaria()
        ja2.dynamic_input("qual o comprimento da barra?", "english", 0)
        ja2.dynamic_input2("qual o deslocamento inicial?", "français")
        grafico1 = ja2.mycgx("imagem.png", "descrição do gráfico 1", "français")
        grafico2 = ja2.mycgx("imagem2.png", "descrição do gráfico 2", "français")
        # ... quantos campos/imagens quiser, tudo na mesma janela ...
        L, D = ja2.aguardar_confirmacao()

    dynamic_input(question, language, min, idioma_origem=None):
        adiciona um campo que exige valor MAIOR que `min`.

    dynamic_input2(question, language, idioma_origem=None):
        adiciona um campo SEM limite mínimo nem máximo — qualquer número
        válido (inclusive negativo ou zero) é aceito.

    mycgx(imagem, description, langue, idioma_origem=None):
        adiciona uma imagem (procurada na mesma pasta do script __file__) com
        uma descrição traduzida pra `langue`, numa galeria/carrossel com
        botões "<" e ">" pra navegar entre as N imagens adicionadas, e zoom
        via scroll do mouse sobre a imagem. Não bloqueia, não conta pra
        validação do botão OK (é só um visualizador, não um input).

    downloadinp(Bname, language, idioma_origem=None):
        adiciona um botão (texto traduzido pra `language`) que, ao clicar,
        pergunta qual extensão baixar (12D, CVG, DAT, FRD, INP, OUT, STA) e
        depois abre um "Salvar como" (nome sugerido "model.<extensão>") pra o
        usuário escolher pasta e nome. Não bloqueia, não conta pra validação
        do botão OK.

    downloadpng(Bname, language, idioma_origem=None):
        adiciona um botão (texto traduzido pra `language`) que, ao clicar,
        copia todos os .png de SCRIPT_DIR (exceto os com "logo" no nome) pra
        a pasta escolhida, renomeando cada cópia como "graph01.png",
        "graph02.png", etc. Os arquivos originais nunca são renomeados.

    Nenhum dos métodos acima bloqueia nem retorna valor na hora. aguardar_confirmacao()
    mostra a janela e BLOQUEIA até o usuário preencher TODOS os campos
    dynamic_input/dynamic_input2 com valores válidos e clicar OK. Retorna os
    valores na mesma ordem em que os campos foram declarados (as imagens da
    galeria não entram nesse retorno).
    """

    def __init__(self):
        super().__init__()
        self._campos = []      # lista de dicts: {"cell": QLineEdit, "minimo": float, "maximo": float}
        self._loop = None

        # --- galeria de imagens (mycgx) ---
        self._imagens = []          # lista de dicts: {"caminho", "descricao_original", "idioma", "texto_traduzido", "pendente", "pixmap"}
        self._indice_imagem_atual = -1
        self._zoom = 1.0

        # --- spinner de carregamento (enquanto a tradução de um campo/imagem não chega) ---
        self._spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_indice = 0
        self._pendentes = set()  # widgets (labels) que ainda estão esperando tradução
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(120)
        self._spinner_timer.timeout.connect(self._atualizar_spinner)

        self._fila_tradutor = FilaTradutorWorker()
        self._fila_tradutor.pronto.connect(self._on_traducao_pronta)
        self._fila_tradutor.start()

        self.setWindowTitle("TurboFEM — Values")
        self.setMinimumSize(760, 560)
        self.resize(860, 720)

        self._fundo = None
        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))
            pix = QPixmap(str(LOGO_PATH))
            if not pix.isNull():
                self._fundo = pix

        layout_geral = QVBoxLayout(self)
        layout_geral.setContentsMargins(50, 40, 50, 30)
        layout_geral.setSpacing(20)

        titulo = QLabel("TurboFEM")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        titulo.setStyleSheet("color: rgba(220, 200, 255, 235); letter-spacing: 4px;")
        layout_geral.addWidget(titulo)

        # área rolável dos campos, pois o número de campos é dinâmico (você decide quantos)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._scroll.viewport().setStyleSheet("background: transparent;")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._campos_layout = QVBoxLayout(self._container)
        self._campos_layout.setSpacing(22)
        self._campos_layout.addStretch()
        self._scroll.setWidget(self._container)
        layout_geral.addWidget(self._scroll, stretch=1)

        # ---------- galeria de imagens (mycgx) — começa escondida até a 1ª imagem ----------
        self._galeria_container = QWidget()
        self._galeria_container.setVisible(False)
        galeria_layout = QVBoxLayout(self._galeria_container)
        galeria_layout.setContentsMargins(0, 0, 0, 0)
        galeria_layout.setSpacing(10)

        self._label_descricao_imagem = QLabel("")
        self._label_descricao_imagem.setAlignment(Qt.AlignCenter)
        self._label_descricao_imagem.setWordWrap(True)
        self._label_descricao_imagem.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self._label_descricao_imagem.setStyleSheet("color: #ffffff;")
        sombra_desc = QGraphicsDropShadowEffect()
        sombra_desc.setBlurRadius(22)
        sombra_desc.setOffset(0, 2)
        sombra_desc.setColor(QColor(0, 0, 0, 230))
        self._label_descricao_imagem.setGraphicsEffect(sombra_desc)
        galeria_layout.addWidget(self._label_descricao_imagem)

        linha_navegacao = QHBoxLayout()
        linha_navegacao.setSpacing(14)

        self._botao_anterior = QPushButton("<")
        self._botao_anterior.setCursor(Qt.PointingHandCursor)
        self._botao_anterior.setFixedSize(44, 220)
        self._botao_anterior.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._botao_anterior.setStyleSheet(self._estilo_botao_navegacao())
        self._botao_anterior.clicked.connect(self._imagem_anterior)
        linha_navegacao.addWidget(self._botao_anterior)

        self._label_imagem = _ImagemComZoom(self._on_wheel_zoom_imagem)
        self._label_imagem.setAlignment(Qt.AlignCenter)
        self._label_imagem.setStyleSheet("background: transparent; color: rgba(255,255,255,180);")

        self._scroll_imagem = QScrollArea()
        self._scroll_imagem.setWidgetResizable(False)  # permite a imagem crescer com o zoom e a scroll area dar pan
        self._scroll_imagem.setFixedHeight(320)
        self._scroll_imagem.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._scroll_imagem.setWidget(self._label_imagem)
        self._scroll_imagem.setAlignment(Qt.AlignCenter)
        linha_navegacao.addWidget(self._scroll_imagem, stretch=1)

        self._botao_proximo = QPushButton(">")
        self._botao_proximo.setCursor(Qt.PointingHandCursor)
        self._botao_proximo.setFixedSize(44, 220)
        self._botao_proximo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._botao_proximo.setStyleSheet(self._estilo_botao_navegacao())
        self._botao_proximo.clicked.connect(self._imagem_proxima)
        linha_navegacao.addWidget(self._botao_proximo)

        galeria_layout.addLayout(linha_navegacao)

        dica_zoom = QLabel("scroll do mouse sobre a imagem = zoom")
        dica_zoom.setAlignment(Qt.AlignCenter)
        dica_zoom.setStyleSheet("color: rgba(255,255,255,140); font-size: 11px;")
        galeria_layout.addWidget(dica_zoom)

        layout_geral.addWidget(self._galeria_container)

        # ---------- botões de download (downloadinp / downloadpng) ----------
        self._downloads_container = QWidget()
        self._downloads_layout = QVBoxLayout(self._downloads_container)
        self._downloads_layout.setContentsMargins(0, 0, 0, 0)
        self._downloads_layout.setSpacing(10)
        layout_geral.addWidget(self._downloads_container)

        self.botao_ok = QPushButton("OK")
        self.botao_ok.setCursor(Qt.PointingHandCursor)
        self.botao_ok.setMinimumHeight(50)
        self.botao_ok.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        self.botao_ok.setEnabled(False)
        self.botao_ok.setStyleSheet(self._estilo_botao())
        self.botao_ok.clicked.connect(self._confirmar)
        layout_geral.addWidget(self.botao_ok)

        rodape = QLabel("TurboFEM · Finite Element Method — Vinícius José Martins Coutinho")
        rodape.setAlignment(Qt.AlignCenter)
        rodape.setStyleSheet("color: rgba(255,255,255,150); font-size: 12px; letter-spacing: 1px;")
        layout_geral.addWidget(rodape)

    # ---------- fundo com a imagem ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        if self._fundo is not None:
            escalado = self._fundo.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - escalado.width()) // 2
            y = (self.height() - escalado.height()) // 2
            painter.drawPixmap(x, y, escalado)
        else:
            painter.fillRect(self.rect(), QColor("#0d0d12"))
        painter.fillRect(self.rect(), QColor(8, 8, 16, 190))
        painter.end()
        super().paintEvent(event)

    @staticmethod
    def _estilo_botao():
        return """
            QPushButton {
                background-color: rgba(148, 92, 255, 160);
                border: 1.5px solid rgba(148, 92, 255, 220);
                border-radius: 12px;
                color: #ffffff;
            }
            QPushButton:hover:!disabled {
                background-color: rgba(148, 92, 255, 210);
            }
            QPushButton:disabled {
                background-color: rgba(120, 120, 120, 70);
                border: 1.5px solid rgba(150, 150, 150, 90);
                color: rgba(255,255,255,110);
            }
        """

    @staticmethod
    def _estilo_botao_navegacao():
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 18);
                border: 1.5px solid rgba(148, 92, 255, 160);
                border-radius: 10px;
                color: #f2f0ff;
            }
            QPushButton:hover:!disabled {
                background-color: rgba(148, 92, 255, 95);
            }
            QPushButton:disabled {
                background-color: rgba(120, 120, 120, 40);
                border: 1.5px solid rgba(150, 150, 150, 70);
                color: rgba(255,255,255,90);
            }
        """

    # ---------- spinner de carregamento (compartilhado entre campos e a galeria) ----------
    def _atualizar_spinner(self):
        if not self._pendentes:
            self._spinner_timer.stop()
            return
        self._spinner_indice = (self._spinner_indice + 1) % len(self._spinner_frames)
        frame = self._spinner_frames[self._spinner_indice]
        for widget in self._pendentes:
            widget.setText(f"{frame}  Loading...")

    def _on_traducao_pronta(self, alvo, texto):
        if isinstance(alvo, dict) and alvo.get("tipo") == "imagem":
            self._on_traducao_pronta_imagem(alvo["indice"], texto)
            return

        # caso padrão: alvo é um QLabel de um dynamic_input/dynamic_input2
        self._pendentes.discard(alvo)
        alvo.setText(texto)
        if not self._pendentes:
            self._spinner_timer.stop()

    # ================= CAMPOS (dynamic_input / dynamic_input2) =================

    # ---------- helper privado: cria o bloco (label + célula) compartilhado pelos dois métodos públicos ----------
    def _criar_bloco_campo(self, question, language, idioma_origem, minimo, maximo):
        label_pergunta = QLabel(f"{self._spinner_frames[0]}  Loading...")  # nunca mostra o texto original
        label_pergunta.setAlignment(Qt.AlignCenter)
        label_pergunta.setWordWrap(True)
        label_pergunta.setFont(QFont("Segoe UI", 18, QFont.Bold))
        label_pergunta.setStyleSheet("color: #ffffff;")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(24)
        sombra.setOffset(0, 2)
        sombra.setColor(QColor(0, 0, 0, 230))
        label_pergunta.setGraphicsEffect(sombra)

        celula = QLineEdit()
        celula.setAlignment(Qt.AlignCenter)
        celula.setFixedSize(160, 38)
        celula.setFont(QFont("Calibri", 13))
        celula.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #b7b7b7;
                border-radius: 0px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        validador = QRegularExpressionValidator(QRegularExpression(r"^-?\d*[.,]?\d*$"))
        celula.setValidator(validador)
        celula.textChanged.connect(self._revalidar_tudo)

        wrapper_celula = QHBoxLayout()
        wrapper_celula.addStretch()
        wrapper_celula.addWidget(celula)
        wrapper_celula.addStretch()

        bloco = QVBoxLayout()
        bloco.setSpacing(8)
        bloco.addWidget(label_pergunta)
        bloco.addLayout(wrapper_celula)

        # insere antes do addStretch() final do container
        self._campos_layout.insertLayout(self._campos_layout.count() - 1, bloco)

        self._campos.append({"cell": celula, "minimo": minimo, "maximo": maximo})

        self._pendentes.add(label_pergunta)
        if not self._spinner_timer.isActive():
            self._spinner_timer.start()

        self._fila_tradutor.enfileirar(question, language, label_pergunta, idioma_origem=idioma_origem)

        self._revalidar_tudo()

    # ---------- API pública: adicionar um campo COM mínimo (não bloqueia) ----------
    def dynamic_input(self, question, language, min, idioma_origem=None):
        """
        Adiciona um novo campo (pergunta + célula estilo Excel) na MESMA janela,
        exigindo um valor MAIOR que `min`. Não bloqueia e não retorna valor —
        os valores só ficam disponíveis depois que aguardar_confirmacao() for
        chamado e o usuário clicar OK.

        idioma_origem: opcional. Se None (padrão), o motor_tradutor detecta
        sozinho o idioma da pergunta via langdetect. Só passe esse parâmetro
        se você quiser FORÇAR manualmente o idioma de origem numa chamada
        específica (ex: se souber que o langdetect está errando naquela frase).
        """
        self._criar_bloco_campo(question, language, idioma_origem, minimo=float(min), maximo=None)

    # ---------- API pública: adicionar um campo SEM mínimo nem máximo (não bloqueia) ----------
    def dynamic_input2(self, question, language, idioma_origem=None):
        """
        Igual ao dynamic_input(), mas SEM limite mínimo nem máximo — qualquer
        número válido (inteiro, decimal, negativo, zero) é aceito. O único
        requisito é que a célula contenha um número que dê pra converter em
        float; enquanto estiver vazia ou com texto inválido, o botão OK
        continua desabilitado (assim como nos campos com limite).
        """
        self._criar_bloco_campo(question, language, idioma_origem, minimo=None, maximo=None)

    # ---------- validação global: TODOS os campos precisam estar válidos ----------
    def _revalidar_tudo(self, *_args):
        if not self._campos:
            self.botao_ok.setEnabled(False)
            return

        for campo in self._campos:
            texto_atual = campo["cell"].text().strip().replace(",", ".")
            try:
                valor = float(texto_atual)
            except ValueError:
                self.botao_ok.setEnabled(False)
                return
            if campo["minimo"] is not None and not (valor > campo["minimo"]):
                self.botao_ok.setEnabled(False)
                return
            if campo["maximo"] is not None and not (valor < campo["maximo"]):
                self.botao_ok.setEnabled(False)
                return

        self.botao_ok.setEnabled(True)

    # ================= GALERIA DE IMAGENS (mycgx) =================

    def mycgx(self, imagem, description, langue, idioma_origem=None):
        """
        Adiciona uma imagem (procurada na mesma pasta do script __file__) com
        uma descrição traduzida pra `langue`, numa galeria/carrossel na MESMA
        janela. Não bloqueia e não retorna valor de input — é só um
        visualizador (não conta pra validação do botão OK).

        imagem: nome do arquivo (ex: "imagem.png"), procurado em SCRIPT_DIR.
        description: texto da descrição, no idioma original em que você escreveu.
        langue: idioma de destino (chave do dicionário IDIOMAS), pra onde a
            descrição será traduzida.
        idioma_origem: opcional, mesmo comportamento do dynamic_input.

        Use várias vezes (mycgx chamado N vezes) pra ter N imagens navegáveis
        com "<" e ">". Zoom: scroll do mouse sobre a imagem.
        """
        caminho = SCRIPT_DIR / imagem
        pixmap = None
        if caminho.exists():
            candidato = QPixmap(str(caminho))
            if not candidato.isNull():
                pixmap = candidato

        registro = {
            "caminho": caminho,
            "descricao_original": description,
            "idioma": langue,
            "texto_traduzido": None,
            "pendente": True,
            "pixmap": pixmap,
        }
        indice = len(self._imagens)
        self._imagens.append(registro)

        alvo = {"tipo": "imagem", "indice": indice}
        self._fila_tradutor.enfileirar(description, langue, alvo, idioma_origem=idioma_origem)

        if indice == 0:
            self._galeria_container.setVisible(True)
            self._ir_para_imagem(0)
        else:
            self._atualizar_botoes_navegacao()

        return registro

    def _on_traducao_pronta_imagem(self, indice, texto):
        if indice >= len(self._imagens):
            return
        self._imagens[indice]["texto_traduzido"] = texto
        self._imagens[indice]["pendente"] = False

        if indice == self._indice_imagem_atual:
            self._pendentes.discard(self._label_descricao_imagem)
            self._label_descricao_imagem.setText(texto)
            if not self._pendentes:
                self._spinner_timer.stop()

    def _ir_para_imagem(self, indice):
        if not (0 <= indice < len(self._imagens)):
            return
        self._indice_imagem_atual = indice
        self._zoom = 1.0
        registro = self._imagens[indice]

        self._atualizar_pixmap_exibido()

        if registro["pendente"]:
            self._pendentes.add(self._label_descricao_imagem)
            if not self._spinner_timer.isActive():
                self._spinner_timer.start()
            frame = self._spinner_frames[self._spinner_indice]
            self._label_descricao_imagem.setText(f"{frame}  Loading...")
        else:
            self._pendentes.discard(self._label_descricao_imagem)
            self._label_descricao_imagem.setText(registro["texto_traduzido"])

        self._atualizar_botoes_navegacao()

    def _atualizar_botoes_navegacao(self):
        self._botao_anterior.setEnabled(self._indice_imagem_atual > 0)
        self._botao_proximo.setEnabled(self._indice_imagem_atual < len(self._imagens) - 1)

    def _imagem_anterior(self):
        if self._indice_imagem_atual > 0:
            self._ir_para_imagem(self._indice_imagem_atual - 1)

    def _imagem_proxima(self):
        if self._indice_imagem_atual < len(self._imagens) - 1:
            self._ir_para_imagem(self._indice_imagem_atual + 1)

    # ---------- zoom (scroll do mouse sobre a imagem) ----------
    def _on_wheel_zoom_imagem(self, delta):
        if delta > 0:
            self._zoom *= 1.15
        else:
            self._zoom /= 1.15
        self._zoom = max(0.2, min(self._zoom, 6.0))
        self._atualizar_pixmap_exibido()

    def _atualizar_pixmap_exibido(self):
        if not (0 <= self._indice_imagem_atual < len(self._imagens)):
            self._label_imagem.setPixmap(QPixmap())
            self._label_imagem.setText("")
            return

        registro = self._imagens[self._indice_imagem_atual]
        pixmap = registro["pixmap"]

        if pixmap is None:
            self._label_imagem.setPixmap(QPixmap())
            self._label_imagem.setText(f"[imagem não encontrada: {registro['caminho'].name}]")
            self._label_imagem.resize(self._label_imagem.sizeHint())
            return

        novo_tamanho = QSize(int(pixmap.width() * self._zoom), int(pixmap.height() * self._zoom))
        escalado = pixmap.scaled(novo_tamanho, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._label_imagem.setText("")
        self._label_imagem.setPixmap(escalado)
        self._label_imagem.resize(escalado.size())

    # ================= DOWNLOAD DE ARQUIVOS (downloadinp / downloadpng) =================

    EXTENSOES_INP = ["12D", "CVG", "DAT", "FRD", "INP", "OUT", "STA"]

    def _criar_botao_acao(self, Bname, language, idioma_origem, callback_click):
        botao = QPushButton(f"{self._spinner_frames[0]}  Loading...")  # nunca mostra o texto original
        botao.setCursor(Qt.PointingHandCursor)
        botao.setMinimumHeight(48)
        botao.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        botao.setStyleSheet(self._estilo_botao())
        botao.clicked.connect(callback_click)
        self._downloads_layout.addWidget(botao)

        self._pendentes.add(botao)
        if not self._spinner_timer.isActive():
            self._spinner_timer.start()

        self._fila_tradutor.enfileirar(Bname, language, botao, idioma_origem=idioma_origem)

        return botao

    def downloadinp(self, Bname, language, idioma_origem=None):
        """
        Adiciona um botão (texto `Bname` traduzido pra `language`). Ao clicar:
        1) Abre um diálogo perguntando qual extensão baixar, entre
           12D, CVG, DAT, FRD, INP, OUT ou STA (procuradas em SCRIPT_DIR).
        2) Abre um "Salvar como" (igual Ctrl+Shift+S de qualquer programa),
           sugerindo o nome "model.<extensão>" — o usuário pode mudar o nome
           e escolher a pasta livremente.
        Não bloqueia, não conta pra validação do botão OK.
        """
        def ao_clicar():
            pergunta = motor_tradutor(
                "Qual tipo de arquivo você quer baixar?", language, idioma_origem=idioma_origem
            )
            dialogo = _DialogoEscolherExtensao(pergunta, self.EXTENSOES_INP, parent=self)
            if dialogo.exec() != QDialog.Accepted or dialogo.extensao_escolhida is None:
                return  # usuário cancelou a escolha da extensão

            extensao = dialogo.extensao_escolhida
            caminho_origem = self._encontrar_arquivo_por_extensao(extensao)
            if caminho_origem is None:
                print(f"[downloadinp] nenhum arquivo .{extensao.lower()} encontrado em {SCRIPT_DIR}")
                return

            nome_sugerido = f"model.{extensao.lower()}"
            filtro = f"Arquivo {extensao} (*.{extensao.lower()});;Todos os arquivos (*)"
            caminho_escolhido, _ = QFileDialog.getSaveFileName(
                self, "Salvar como", str(Path.home() / nome_sugerido), filtro
            )
            if not caminho_escolhido:
                return  # usuário cancelou o "salvar como"

            try:
                shutil.copy2(caminho_origem, caminho_escolhido)
                print(f"[downloadinp] arquivo salvo em: {caminho_escolhido}")
            except Exception as e:
                print(f"[downloadinp] erro ao copiar: {e}")

        return self._criar_botao_acao(Bname, language, idioma_origem, ao_clicar)

    def downloadpng(self, Bname, language, idioma_origem=None):
        """
        Adiciona um botão (texto `Bname` traduzido pra `language`). Ao clicar,
        abre um seletor de pasta e copia todos os .png de SCRIPT_DIR (exceto
        os que têm "logo" no nome) pra lá, RENOMEANDO cada cópia como
        "graph01.png", "graph02.png", ... na ordem alfabética dos originais.
        Os arquivos originais na pasta do script NÃO são renomeados nem alterados
        — só as cópias na pasta escolhida pelo usuário recebem o novo nome.
        Não bloqueia, não conta pra validação do botão OK.
        """
        def ao_clicar():
            pasta_destino = QFileDialog.getExistingDirectory(self, "Escolha a pasta de destino")
            if not pasta_destino:
                return  # usuário cancelou

            pasta_destino = Path(pasta_destino)
            arquivos = [
                a for a in sorted(SCRIPT_DIR.glob("*.png"))
                if "logo" not in a.stem.lower()
            ]
            if not arquivos:
                print(f"[downloadpng] nenhum .png (sem 'logo' no nome) encontrado em {SCRIPT_DIR}")
                return

            largura = max(2, len(str(len(arquivos))))
            copiados = []
            for i, arquivo in enumerate(arquivos, start=1):
                novo_nome = f"graph{i:0{largura}d}.png"
                try:
                    shutil.copy2(arquivo, pasta_destino / novo_nome)
                    copiados.append(novo_nome)
                except Exception as e:
                    print(f"[downloadpng] erro ao copiar {arquivo.name}: {e}")

            print(f"[downloadpng] {len(copiados)} imagem(ns) copiada(s) e renomeada(s) em {pasta_destino}: {copiados}")

        return self._criar_botao_acao(Bname, language, idioma_origem, ao_clicar)

    def _encontrar_arquivo_por_extensao(self, extensao):
        extensao_lower = extensao.lower()
        for arquivo in sorted(SCRIPT_DIR.iterdir()):
            if arquivo.is_file() and arquivo.suffix.lower() == f".{extensao_lower}":
                return arquivo
        return None

    # ---------- clique do botão OK ----------
    def _confirmar(self):
        if not self.botao_ok.isEnabled():
            return
        if self._loop is not None:
            self._loop.quit()

    # ---------- API pública: mostra a janela e espera TODOS os campos + clique OK ----------
    def aguardar_confirmacao(self):
        """
        Mostra a janela (se ainda não estiver visível) e bloqueia até o usuário
        preencher TODOS os campos declarados via dynamic_input()/dynamic_input2()
        com valores válidos e clicar em OK. Retorna uma lista com os valores,
        na mesma ordem em que os campos foram declarados. Imagens da galeria
        (mycgx) não entram nesse retorno nem afetam a validação do OK.
        """
        if not self.isVisible():
            self.show()

        self._revalidar_tudo()

        self._loop = QEventLoop()
        self._loop.exec()
        self._loop = None

        valores = []
        for campo in self._campos:
            texto_atual = campo["cell"].text().strip().replace(",", ".")
            try:
                valores.append(float(texto_atual))
            except ValueError:
                valores.append(None)
        return valores

    # ---------- fechar no X também libera o loop e para a fila, evitando travar ----------
    def closeEvent(self, event):
        if self._loop is not None:
            self._loop.quit()
        self._fila_tradutor.parar()
        self._fila_tradutor.wait(2000)
        super().closeEvent(event)

#function that start code's interface
def try_the_interface():
    try:
        #only try...
        my_return = QApplication(sys.argv)
        return my_return
    except Exception as e:
        print(f"Erro: {e}")
        return None

#geometry 1D
def main2():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    ja2.dynamic_input("what's the beam's length \n (at unity [mm])?", langue, 0)
    ja2.dynamic_input('how many "B31" elements?', langue, 0)
    
    L, N_e = ja2.aguardar_confirmacao()
    
    ja2.close()
    
    script = "testgeo2.py"
    #replace lines
    old_line = "    L = 150"
    new_line = f"    L = {L}"
    old_line2 = "    n_nodes_raw = 15"
    new_line2 = f"    n_nodes_raw = {N_e}"#+"\n"+"N_NODES = int(math.ceil((N_NODES+1)))"
    
    changesA2B = [
    ( f"{old_line}" , new_line),
    ( f"{old_line2}" , new_line2)]

    dirLN = try_copy_and_change_script2(script, changesA2B)
    return L, N_e
    
#E,nu,...
def main3():
    keys = readkeys()
    langue = speakit(keys)

    material_tupla = selecionar_material2()
    
    ja3 = JanelaSecundaria()

    ja3.dynamic_input(f"{material_tupla}", langue, 0)
    #ja3.dynamic_input("how many elements?", langue, 0)
    M_e = ja3.aguardar_confirmacao()
    M_eb = M_e[0]
    M_eb = math.ceil(M_eb)
    if float(M_eb) > 16:
        M_eb = 16
    

    ja3.close()
    return [M_eb]

def submain3(first_input):
    keys = readkeys()
    langue = speakit(keys)
    if(float(first_input)>4):
        v1 = True
        if(float(first_input)>15):
            another = True
        else:
            another = False


    if(float(first_input)<5):
        submaterial_tupla = selecionar_material3(first_input)
        ja3b = JanelaSecundaria()
        ja3b.dynamic_input(f"{submaterial_tupla}", langue, 0)
        ja3b.close()
        Mf = ja3b.aguardar_confirmacao()
        if(float(first_input)==1):
            if(float(f"{int(math.ceil(float(f'{Mf[0]}')))}")>8):
                first_input = "16"
                another = True
                v1 = True
                
        if(float(first_input)==2):
            if(float(f"{int(math.ceil(float(f'{Mf[0]}')))}")>8):
                first_input = "16"
        
        #
        return selecionar_material3b(first_input,f"{int(math.ceil(float(f'{Mf[0]}')))}")    
    if(v1):
        if((another)):
            ja3c = JanelaSecundaria()
            other = "X"
            #E
            ja3c.dynamic_input('digite aqui o valor do Módulo de elasticidade ("E") do material na unidade de [MPa]:', langue, 0)
            #ν (nu)
            ja3c.dynamic_input(r'digite aqui o valor do coeficiente de Poisson("ν") do material:', langue, 0)
            #density
            ja3c.dynamic_input(r'digite aqui o valor do coeficiente da densidade ("ρ") do material na udnidade de [toneladas/mm³]:', langue, 0)
            #cp
            ja3c.dynamic_input(r'digite aqui o valor do coeficiente do calor especifico cp do material na unidade de [mJ/(ton·K)]:', langue, 0)
            #k
            ja3c.dynamic_input(r'digite aqui o valor da condutibilidade termica k do material na unidade de [mW/(mm·K)]:', langue, 0)
            #α
            ja3c.dynamic_input(r'digite aqui o valor do coeficiente de dilatação ("α") do material na unidade de [1/K]:', langue, 0)
            E, nu, ro, cp, kmaterial, alpha = ja3c.aguardar_confirmacao()
            ja3c.close()
            return other, E, min(0.49999999, nu), ro, cp, kmaterial, alpha                                    
        else:
            return selecionar_material3b(first_input,f"{int(math.ceil(float(f'{1}')))}")#MATERIAIS_SIMPLES[first_input]

        submaterial_tupla = selecionar_material3(first_input)
        ja3b = JanelaSecundaria()
        ja3b.dynamic_input(f"{submaterial_tupla}", langue, 0)
        ja3b.close()
    #
    return M_eb

def subsubmain3(first_input):
    #print(f"first_input = {first_input}")
    others2 = submain3(first_input)
    #print(f"outro = {others2}")
    try:
        others2 = f"{int(others2[0])}"        
    except:
        try:
            others2 = f"{int(others2)}"
        except:
            return others2
        #others2 = f"{int(others2[0])}"
        

    if(float(others2) < 5):
        return (submain3("16"))
    else:
        #
        return others2

def mainterial():
    #resultado->first material
    resultado = main3()
    
    #..., E, nu, ro, cp, alpha = subresultado
    subresultado = subsubmain3(f"{int(resultado[0])}")

    #replace
    script2 = "editar_inp_material_secao2_copy.py"
    old_line = "    material_tupla = selecionar_material()"
    new_line = f"    material_tupla = {subresultado}"
    
    changesA2B = [( f"{old_line}" , new_line)]

    dirmaterial2 = try_copy_and_change_script2(script2, changesA2B) 
    return subresultado

#A,Ix,Iy,Iz,Jxy
def main4cross():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    strcross = definir_secao2()
    ja2.dynamic_input(strcross, langue, 0)
    #ja2.dynamic_input("how many elements?", langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    cross2D = cross2D[0]
    if(cross2D > 5):
        cross2D = 5
    cross2D = f"{int(math.ceil(float(cross2D)))}"
    return cross2D

#1) b+h
def main4cross1():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    sr1 = ("Seção retangular... Digite a base e altura em [mm].")
    sr2 = ("\n\nBase  b [mm]: ")
    sr3 = sr1 + sr2
    ja2.dynamic_input(sr3, langue, 0)
    ja2.dynamic_input(("Altura h [mm]: "), langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    b = cross2D[0]
    h = cross2D[1]
    sqs =  _secao_retangular2(b,h)
        
    return sqs

#2) d = 2r
def main4cross2():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    sc1 = ("Seção circular compacta... \n\nDigite aqui o \nvalor do diâmetro em [mm]:")
    
    ja2.dynamic_input(sc1, langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()

    cross2D = _secao_circular_cheia2(cross2D[0]) 
    
    
        
    return cross2D

#3) d_max+d_min
def main4cross3a():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    
    sct01 = ("Seção circular tubular (tubo)...\n  Diâmetro externo e interno em [mm].\n\n")
    sct02 = ("Diâmetro externo D em [mm]: ")
    sct03 = ("Diâmetro interno d em [mm]: ")
    
    ja2.dynamic_input( (sct01 + sct03) , langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()

    #d_max = cross2D[0]
    d_min = cross2D[0]
    #sqs = _secao_circular_tubular2(d_max,d_min) 
    
    return d_min #sqs

def main4cross3b(d_min):
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    
    sct01 = (f"Seção circular tubular (tubo)...\n  Diâmetro externo e interno em [mm].\n\n")
    sct02 = ("Diâmetro externo D em [mm]: ")
    sct03 = ("Diâmetro interno d em [mm]: ")
    
    ja2.dynamic_input( (sct01 + sct02) , langue, d_min)
    #ja2.dynamic_input(sct03 , langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()

    d_max = cross2D[0]
    #d_min = cross2D[1]
    sqs = _secao_circular_tubular2(d_max,d_min) #_secao_circular_tubular2(d_max,d_min)
        
    return sqs

def main4cross3c():
    d_min = main4cross3a()
    tube = main4cross3b(d_min)
    return tube
    
#4)i's beam
def main4cross4b():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    istr1 = ("Secao tipo I (viga I simplificada)...\n dimensões em [mm].\n\n")
    istr2 = ""#("\n largura (bf), altura total (h), espessura da largura (tf),")
    istr3 = ""#("\n espessura da altura (tw)\n\n")
    istr4 =("Largura bf [mm]: ")
    istr5 = istr1 + istr2 + istr3 + istr4
    istr6 = ("Altura total h [mm]: ")
    istr7 = ("Espessura da largura tf [mm]: ")
    istr8 = ("Espessura da altura tw [mm]: ")
    
    ja2.dynamic_input(istr5, langue, 0)
    ja2.dynamic_input(istr6, langue, 0)
    ja2.dynamic_input(istr7, langue, 0)
    ja2.dynamic_input(istr8, langue, 0)
    
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    
    bf = cross2D[0]
    h = cross2D[1]
    tf = cross2D[2]
    tw = cross2D[3]
    
    cross2D = _secao_perfil_i2(bf, h, tf, tw) 
           
    return cross2D

def main4cross4():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()
    istr1 = ("Secao tipo I (viga I simplificada)...\n dimensões em [mm].\n\n")
    istr2 = ""#("\n largura (bf), altura total (h), espessura da largura (tf),")
    istr3 = ""#("\n espessura da altura (tw)\n\n")
    istr4 =("Largura bf [mm]: ")
    istr5 = istr1 + istr2 + istr3 + istr4
    istr6 = ("Altura total h [mm]: ")
    istr7 = ("Espessura da largura tf [mm]: ")
    istr8 = ("Espessura da altura tw [mm]: ")
    
    ja2.dynamic_input(istr5, langue, 0)
    ja2.dynamic_input(istr6, langue, 0)
    ja2.dynamic_input(istr7, langue, 0)
    ja2.dynamic_input(istr8, langue, 0)
    
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    
    bf = cross2D[0]
    h = cross2D[1]
    tf = cross2D[2]
    tw = cross2D[3]
    
    cross2D = _secao_perfil_i2(bf, h, tf, tw) 
           
    return cross2D
    
#5)A, Ixyz 
def main4cross5():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    straixyz = ("Digite os valores de A, Iy, Iz e J \n diretamente (em mm² e mm^4).\n\n")
    A = ("A área da secção transversal A [mm²]: ")
    Iy = ("Momento de inércia Iy (flexão, eixo 2) [mm^4]: ")
    Iz = ("Momento de inércia Iz (flexão, eixo 3) [mm^4]: ")
    J = ("Constante de torção J [mm^4]: ")


    ja2.dynamic_input(straixyz + A, langue, 0)
    ja2.dynamic_input(Iy, langue, 0)
    ja2.dynamic_input(Iz, langue, 0)
    ja2.dynamic_input(J, langue, 0)
    
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    
    Azy = cross2D[0]
    Iyy = cross2D[1]
    Izz = cross2D[2]
    Jxx = cross2D[3]
    
    cross2D = _secao_valores_diretos2(Azy,Iyy,Izz,Jxx)#_secao_perfil_i2(bf, h, tf, tw) 
           
    #return cross2D
    #return {"A": cross2D[0], "Iy": cross2D[1], "Iz": cross2D[2], "J": cross2D[3], "descricao": "Valores digitados diretamente"}
    #return _secao_valores_diretos2(A,Iy,Iz,J)
    return cross2D
    
    
    
#1+2+3+4+5)A, Ixyz 
#geo2Dzy
def main4crossf():
    choice2 = main4cross()

    if(choice2 == "1"):
        thecross = main4cross1()
    #
    if(choice2 == "2"):
        thecross = main4cross2()
    #
    if(choice2 == "3"):
        thecross = main4cross3c()
    #
    if(choice2 == "4"):
        thecross = main4cross4()
    #
    if(choice2 == "5"):
        thecross = main4cross5()
        #thecross2 =  {"A": thecross[0], "Iy": thecross[1], "Iz": thecross[2], "J": thecross[3], "descricao": "Valores digitados diretamente"}
    #
    
    
    
    script = "editar_inp_material_secao2.py"
    #replace lines
    old_line = "    secao_dict = definir_secao()"
    new_line = f"    secao_dict = {thecross}"
    
    
    changesA2B = [( f"{old_line}" , new_line)]

    dircross = try_copy_and_change_script2(script, changesA2B) #
    return thecross


    
#Uf
def main5uf():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    strcross = ("No primeiro nó (x=0), é onde todos deslocamentos e rotações vão estar bloqueados e nulos. ")
    strcross = strcross + ("\n No ultimo nó (x=L), será uma extremidade livre deslocada.")
    strcross =     strcross + (" \n\n Definição do carregamento")     
    strcross =     strcross 
    strcross =     strcross + ("\n\n 1 - Impondo deslocamentos lá no ultimo nó")
    strcross =     strcross + ("\n 2 - Impor esforços (carga distribuida + forças + momentos fletores e torçores no ultimo nó)")
    strcross =     strcross + "\n\n Escolha uma opcão dessas ai em cima:"
    
    
    ja2.dynamic_input(strcross, langue, 0)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()
    cross2D = math.ceil(float(cross2D[0]))
    if(cross2D > 2):
        cross2D = 2
    cross2D = f"{int(math.ceil(float(cross2D)))}"
    return cross2D

#u
def main5ufxyz():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    strcross = (" Modo selecionado: impor deslocamentos no final da viga")
    strcross =     strcross + ("\n O ultimo nó (em x=L) terá deslocamento imposto.")
    strcross =     strcross + ("\n\nDigite os componentes do deslocamento final (em mm).")
    strcross =     strcross + ('\n\n\n digita o valor do \n deslocamento "Ux" (axial) [mm]: ')
    strcross02 = ('\n digita o valor do \n deslocamento "Uy" (transversal) [mm]: ')
    strcross03 = ('\n digita o valor do \n deslocamento "Uz" (transversal) [mm]: ')
        
    ja2.dynamic_input2(strcross, langue)
    ja2.dynamic_input2(strcross02, langue)
    ja2.dynamic_input2(strcross03, langue)
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()

    #replace
    script3 = "carregamento_copy.py"
    old_line01 = '    ux = _ler_float("u_final em X (axial) [mm]: ")'
    old_line02 = '    uy = _ler_float("u_final em Y (transversal) [mm]: ")'
    old_line03 = '    uz = _ler_float("u_final em Z (transversal) [mm]: ")'

    new_line01 = f'    ux = {cross2D[0]}'
    new_line02 = f'    uy = {cross2D[1]}' 
    new_line03 = f'    uz = {cross2D[2]}'

    changesA2B = [
    ( f"{old_line01}" , new_line01),
    ( f"{old_line02}" , new_line02),
    ( f"{old_line03}" , new_line03)]

    
    dirUF = try_copy_and_change_script2(script3, changesA2B)
    
    print(dirUF) 

    
    return cross2D

#f
def main5fm():
    keys = readkeys()
    langue = speakit(keys)
    
    ja2 = JanelaSecundaria()

    strcross = ("Modo selecionado: impor esforços...")
    strcross =     strcross + ("\n Os esforcos são aplicados na seguinte ordem fixa:\n")
    strcross =     strcross + ("\n 1) Carga distribuida uniforme (constante) ao longo de toda a barra")
    strcross =     strcross + ("...\n digite o valor da carga distribuida q [N/mm] \n(perpendicular à essa barra): ")
    strcross02 = ("  2) Força transversal concentrada no no final...")
    strcross02 = strcross02 + ("\n digite o valor da força transversal F [N] (eixo Y local): ")
    strcross03 = ("  3) Força axial concentrada no final...")
    strcross03 = strcross03 +  ("\n digite o valor da força axial F [N] \n(eixo X, paralelo ao comprimento da barra): ")
    strcross04 = ("  4) Moment flechissant concentré sur la fin de la barre...")
    strcross04 = strcross04 +  ("\n  Entrez la valeur du Moment flechissant M [N.mm] \n(autour de l'axe Z sur la fin de la barre): ")
    strcross05 = ("  5) Moment torceur concentré sur la fin de la barre...")
    strcross05 = strcross05 + ("\n Entrez la valeur du moment torceur T [N.mm] \n (couple de torsion autour de l'axe X): ")
 
    
    
    ja2.dynamic_input2(strcross, langue)
    ja2.dynamic_input2(strcross02, langue)
    ja2.dynamic_input2(strcross03, langue)
    ja2.dynamic_input2(strcross04, langue)
    ja2.dynamic_input2(strcross05, langue)
    
    cross2D = ja2.aguardar_confirmacao()
    ja2.close()

    #replace
    script3 = "carregamento_copy.py"
    old_line01 = '    q_dist = _ler_float("Carga distribuida q [N/mm] (perpendicular a barra): ")'
    old_line02 = '    f_transversal = _ler_float("Forca transversal F [N] (eixo Y local): ")'
    old_line03 = '    f_axial = _ler_float("Forca axial F [N] (eixo X, ao longo da barra): ")'
    old_line04 = '    m_fletor = _ler_float("Momento fletor M [N.mm] (em torno do eixo Z): ")'
    old_line05 = '    m_torcor = _ler_float("Momento torçor T [N.mm] (em torno do eixo X, axial): ")'
    
    #new_line01 = f'    ux = {cross2D[0]}'
    #new_line02 = f'    uy = {cross2D[1]}' 
    #new_line03 = f'    uz = {cross2D[2]}'
    new_line01 = f'    q_dist = {cross2D[0]}'
    new_line02 = f'    f_transversal = {cross2D[1]}'
    new_line03 = f'    f_axial = {cross2D[2]}'
    new_line04 = f'    m_fletor = {cross2D[3]}'
    new_line05 = f'    m_torcor = {cross2D[4]}'
   
    

    changesA2B = [
    ( f"{old_line01}" , new_line01),
    ( f"{old_line02}" , new_line02),
    ( f"{old_line03}" , new_line03),
    ( f"{old_line04}" , new_line04),
    ( f"{old_line05}" , new_line05)]

    
    dirUF = try_copy_and_change_script2(script3, changesA2B)
    #print(dirUF)
    
    return cross2D

#displacement or forces  
def main5uqfmt():
    choice2 =  main5uf()
    option21 = choice2

    #replace
    script3 = "carregamento.py"
    
    old_line = '    opcao = input("Escolha uma opcao: ").strip()'
    new_line = f'    opcao = "{choice2}"'

    changesA2B = [( f"{old_line}" , new_line)]
    dirUF = try_copy_and_change_script2(script3, changesA2B) 
    
    #print(dirUF) 

    

    
    if(choice2 == "1"):
        thecross = main5ufxyz()
        return option21, thecross[0], thecross[1], thecross[2]        
    #
    if(choice2 == "2"):
        thecross = main5fm()
        return option21, thecross[0], thecross[1], thecross[2], thecross[3], thecross[4]
        
    
    
    return option21, thecross

#all editors...
def main_editor():
    
    #(ok)step1) L + N_e
    L_N_e = main2()
    L2 = L_N_e[0]
    N2 = L_N_e[1]
    N2 = math.ceil(float(N2))
    N2 = int(N2)
    
     
     
    #(ok)step2a)cross area +...
    cross2D = main4crossf()
    A2 = cross2D['A']
    Iy2 = cross2D['Iy']
    Iz2 = cross2D['Iz']
    J2 = cross2D['J']
     

    #(ok)step2b) material
    propmat = mainterial()
    name, E, nu, ro, cp, kmaterial, alpha = propmat                                    
    #print(dirmaterial)

    #(ok)step3)U xor F
    option21uqfmt = main5uqfmt() 
    option21 = option21uqfmt[0]
    if(option21=="1"):
        return L2,N2,A2,Iy2,Iz2,J2, name, E, nu, ro, cp, kmaterial, alpha, option21, option21uqfmt[1], option21uqfmt[2], option21uqfmt[3]                                    
    #print(f"diruf = {diruf}")
    if(option21=="2"):
        return L2,N2,A2,Iy2,Iz2,J2, name, E, nu, ro, cp, kmaterial, alpha, "2", option21uqfmt[1], option21uqfmt[2], option21uqfmt[3], option21uqfmt[4], option21uqfmt[5]    
    #, option21uqfmt[5]                                                                                                                                                
    
    return L2,N2,A2,Iy2,Iz2,J2, name, E, nu, ro, cp, kmaterial, alpha, option21                                    

#run all..
def main_run_xyz(L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, ux, uy, uz):
    from testgeo2 import main_geo
    from editar_inp_material_secao2_copy_copy import main_edit_material
    from calculomecanico2 import main_ccx
    main_geo(L2,N2)
    cross2D = {"A": A2, "Iy": Iy2, "Iz": Iz2, "J": J2, "descricao": "Valores digitados diretamente"}
    main_edit_material(cross2D,other, E, nu, ro, cp, kmaterial, alpha)
    if(option21=="1"):
        main_ccx(option21,ux,uy,uz,0,0)     
    #

def main_run_qfm(L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, qy, fy, fx, mz, tx):
    from testgeo2 import main_geo
    from editar_inp_material_secao2_copy_copy import main_edit_material
    from calculomecanico2 import main_ccx
    main_geo(L2,N2)
    cross2D = {"A": A2, "Iy": Iy2, "Iz": Iz2, "J": J2, "descricao": "Valores digitados diretamente"}
    main_edit_material(cross2D,other, E, nu, ro, cp, kmaterial, alpha)
    if(option21=="2"):
        main_ccx(option21,qy, fy, fx, mz, tx)
     
    #


#all graphics
def main_cgx():
    #language
    keys = readkeys()
    langue = speakit(keys)

    #call the class
    ja2 = JanelaSecundaria()

    #show plot
    #first-vonmise
    graph00 = ja2.mycgx("geometria_barra_1d_param_deformada.png", "Deformed beam's geometry \n with distorted displacement(ux,uy)", langue)
    graph01 = ja2.mycgx("geometria_barra_1d_param_von_mises.png", "mechanical stress [MPa]\n(Von Mises)", langue)
    graph02 = ja2.mycgx("geometria_barra_1d_param_tresca.png", "The mechanical stress [MPa]\n(Tresca)", langue)
    graph03 = ja2.mycgx("geometria_barra_1d_param_sigma_axial.png", "the beam's mechanical stress [MPa]\n (X axis)", langue)
    graph04 = ja2.mycgx("geometria_barra_1d_param_sigma_max.png", "the maximum beam's main mechanical stress [MPa]", langue)
    graph05 = ja2.mycgx("geometria_barra_1d_param_sigma_min.png", "the minimum beam's main mechanical stress [MPa]", langue)
    graph06 = ja2.mycgx("geometria_barra_1d_param_epsilon_max.png", "The maximum beam's main epslon(STRAIN),\n also known as the beam's maximum main mechacinal deformation \n(epslon = sigma/E)", langue)
    graph07 = ja2.mycgx("geometria_barra_1d_param_epsilon_min.png", "The minimum beam's main epslon(STRAIN),\n also known as the beam's minimum main mechanical deformation \n(epslon = sigma/E)", langue)
    button = ja2.downloadinp("download the model's file here for Abaqus/CalculiX", langue)
    button2 = ja2.downloadpng("download all graphics here", langue)

    #wait...
    ja2.aguardar_confirmacao()

    #end 
    ja2.close()
    
#all steps
def final_main_v1dot0():
    app = try_the_interface() #QApplication(sys.argv)
    #L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, qy, fy, fx, mz, tx = main_editor()
    #L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, ux, uy, uz = main_editor()
    all_data = main_editor()
    L2 = all_data[0]
    N2 = all_data[1]
    A2 = all_data[2]
    Iy2 = all_data[3]
    Iz2 = all_data[4]
    J2  = all_data[5]
    other=all_data[6]
    E   = all_data[7]
    nu  = all_data[8]
    ro  = all_data[9]
    cp  = all_data[10]
    kmaterial=all_data[11]
    alpha=all_data[12]
    option21=all_data[13]
     
    if(all_data[13]=="1"):
        ux  = all_data[14]
        uy  = all_data[15]
        uz  = all_data[16]
        main_run_xyz(L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, ux, uy, uz )
    if(all_data[13]=="2"):
        qy  = all_data[14]
        fy  = all_data[15]
        fx  = all_data[16]
        mz  = all_data[17]
        tx  = all_data[18]
        main_run_qfm(L2,N2,A2,Iy2,Iz2,J2,other, E, nu, ro, cp, kmaterial, alpha, option21, qy, fy, fx, mz, tx )   
            
    graphics = main_cgx()
    print("end of code!")
    print(f"all={all_data}")
    

#"if(True)" only for test...
if(False):

    #here's the main function...
    final_main_v1dot0()
    #end of test