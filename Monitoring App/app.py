# ==================== Complete Siebel Monitoring & Recovery App ====================
# Phases 1-3 integrated
# PyQt5 + oracledb + full core modules + interactive UI
# ---------------- app.py ----------------
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt5.QtGui import QIcon


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/app_icon.png"))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())