import sys
from PySide6.QtWidgets import QApplication
from l4visual.ui.main_window import MainWindow


def main():
    application = QApplication(sys.argv)
    application.setApplicationName('L4D2 Visual VScript')
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == '__main__':
    sys.exit(main())
