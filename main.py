import sys
import PySide6.QtWidgets as QApplication

from MainWindow import MainWindow

app = QApplication(sys.argv)

board = MainWindow()
board.show()

sys.exit(app.exec())
