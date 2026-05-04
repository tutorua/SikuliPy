from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt6.QtCore import Qt, QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#569CD6"))
        keywordFormat.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "def", "class", "if", "elif", "else", "while", "for", 
            "import", "from", "return", "pass", "try", "except", "with", "as"
        ]
        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.highlightingRules.append((pattern, keywordFormat))

        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#CE9178"))
        self.highlightingRules.append((QRegularExpression("\".*\""), stringFormat))
        self.highlightingRules.append((QRegularExpression("'.*'"), stringFormat))

        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#6A9955"))
        self.highlightingRules.append((QRegularExpression("#[^\n]*"), commentFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            matchIterator = pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class PythonEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        font = QFont()
        font.setFamily("Consolas")
        font.setFixedPitch(True)
        font.setPointSize(14)
        self.setFont(font)
        
        # Dark theme colors for the editor
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 5px;
            }
        """)
        
        self.highlighter = PythonHighlighter(self.document())
