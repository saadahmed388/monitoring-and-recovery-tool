from PyQt5.QtCore import pyqtSignal, QObject

class SignalBus(QObject):
    global_signal = pyqtSignal()