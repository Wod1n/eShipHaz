import sys
from PySide6.QtWidgets import QApplication, QFileDialog


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = QFileDialog()
    dialog.show()

    sys.exit(app.exec())
