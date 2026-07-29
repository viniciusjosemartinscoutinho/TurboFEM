# & "C:/Program Files/Python311/python.exe" C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V\Language.py
from pathlib import Path
import os
import sys
import locale
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QGridLayout,
    QVBoxLayout, QGraphicsDropShadowEffect,
)

from motor_tradutor import motor_tradutor, IDIOMAS

SCRIPT_DIR = Path(__file__).resolve().parent
LOGO_PATH = SCRIPT_DIR / "TurboFEM-Logo.png"

# idiomas: codigo ISO -> nome (chave usada no dicionario IDIOMAS)
CODIGO_PARA_NOME = {v: k for k, v in IDIOMAS.items()}

# variantes de locale que precisam de ajuste manual pra bater com o dicionario
ALIAS_CODIGOS = {
    "nb": "no",   # norueguês bokmål
    "nn": "no",   # norueguês nynorsk
    "zh_hans": "zh",
    "zh_hant": "zh",
}


def detectar_idioma_do_sistema():
    """Detecta o idioma nativo do SO e devolve o NOME (chave do dicionário IDIOMAS).
    Se não conseguir detectar ou o idioma do SO não estiver no dicionário, cai pra 'english'.
    """
    codigo_locale = None
    try:
        codigo_locale = locale.getlocale()[0]
    except Exception:
        pass

    if not codigo_locale:
        try:
            codigo_locale = locale.getdefaultlocale()[0]
        except Exception:
            codigo_locale = None

    codigo = "en"
    if codigo_locale:
        codigo = codigo_locale.split("_")[0].lower()

    codigo = ALIAS_CODIGOS.get(codigo, codigo)
    return CODIGO_PARA_NOME.get(codigo, "english")


class TradutorWorker(QThread):
    """Roda a tradução da pergunta em segundo plano, pra não travar a interface
    caso seja a primeira execução (quando os modelos do Argos ainda baixam)."""
    pronto = Signal(str)

    def __init__(self, idioma_destino):
        super().__init__()
        self.idioma_destino = idioma_destino

    def run(self):
        texto = motor_tradutor("What's the language?", self.idioma_destino)
        self.pronto.emit(texto)


class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.langue = None
        self.idioma_pc = detectar_idioma_do_sistema()

        self.setWindowTitle("TurboFEA — Seleção de Idioma")
        self.setMinimumSize(920, 660)
        self.resize(1000, 700)

        self._fundo = None
        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))
            pix = QPixmap(str(LOGO_PATH))
            if not pix.isNull():
                self._fundo = pix

        self._montar_ui()
        self._iniciar_traducao()

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

        # overlay escuro por cima da imagem, pra dar legibilidade ao texto
        painter.fillRect(self.rect(), QColor(8, 8, 16, 190))
        painter.end()
        super().paintEvent(event)

    # ---------- montagem da interface ----------
    def _montar_ui(self):
        layout_geral = QVBoxLayout(self)
        layout_geral.setContentsMargins(60, 46, 60, 40)
        layout_geral.setSpacing(26)

        titulo = QLabel("TurboFEA")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        titulo.setStyleSheet("color: rgba(220, 200, 255, 235); letter-spacing: 4px;")
        layout_geral.addWidget(titulo)

        self.label_pergunta = QLabel("Loading… (first run downloads translation models)")
        self.label_pergunta.setAlignment(Qt.AlignCenter)
        self.label_pergunta.setWordWrap(True)
        self.label_pergunta.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.label_pergunta.setStyleSheet("color: #ffffff;")

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(30)
        sombra.setOffset(0, 3)
        sombra.setColor(QColor(0, 0, 0, 230))
        self.label_pergunta.setGraphicsEffect(sombra)

        layout_geral.addWidget(self.label_pergunta)

        grade = QGridLayout()
        grade.setSpacing(14)

        nomes = list(IDIOMAS.keys())
        colunas = 4
        for i, nome in enumerate(nomes):
            botao = QPushButton(nome.capitalize())
            botao.setCursor(Qt.PointingHandCursor)
            botao.setMinimumHeight(54)
            botao.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
            botao.setStyleSheet(self._estilo_botao())
            botao.clicked.connect(lambda _checked=False, n=nome: self._selecionar_idioma(n))
            linha, coluna = divmod(i, colunas)
            grade.addWidget(botao, linha, coluna)

        layout_geral.addLayout(grade)
        layout_geral.addStretch()

        rodape = QLabel("TurboFEA · Finite Element Analysis — Vinícius José Martins Coutinho")
        rodape.setAlignment(Qt.AlignCenter)
        rodape.setStyleSheet("color: rgba(255,255,255,150); font-size: 12px; letter-spacing: 1px;")
        layout_geral.addWidget(rodape)

    @staticmethod
    def _estilo_botao():
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 18);
                border: 1.5px solid rgba(148, 92, 255, 160);
                border-radius: 12px;
                color: #f2f0ff;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: rgba(148, 92, 255, 95);
                border: 1.5px solid #ba8fff;
            }
            QPushButton:pressed {
                background-color: rgba(98, 52, 200, 170);
            }
        """

    # ---------- tradução da pergunta em segundo plano ----------
    def _iniciar_traducao(self):
        self._worker = TradutorWorker(self.idioma_pc)
        self._worker.pronto.connect(self._on_traducao_pronta)
        self._worker.start()

    def _on_traducao_pronta(self, texto):
        self.label_pergunta.setText(texto)

    # ---------- clique do usuário ----------
    def _selecionar_idioma(self, nome_idioma):
        self.langue = nome_idioma
        self.close()


def main():
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    app.exec()

    langue = janela.langue
    print(langue)
    return langue

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

def main_our_language():
    keys = readkeys()
    langue = speakit(keys)
    lets_choose = True
    if(test_language(langue)):
        lets_choose = False
    if(lets_choose):
        langue = main() 
        save_key(langue, keys)
    #
    return None

#call the function
if(False):
    main_our_language()