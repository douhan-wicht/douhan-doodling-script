import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QColorDialog, QDesktopWidget, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QClipboard, QImage, QPen, QIcon
from PyQt5.QtCore import Qt, QSize, QCoreApplication

class DoodleCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Douhan's Doodling Script")
        self.canvas_size = (1080, 900)  # Larger canvas size
        self.canvas = QImage(*self.canvas_size, QImage.Format_RGB32)
        self.canvas.fill(Qt.white)
        self.last_pos = None
        self.pen_color = Qt.black
        self.pen_width = 6
        self.eraser_mode = False
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Canvas widget
        self.canvas_widget = QWidget()
        layout.addWidget(self.canvas_widget, alignment=Qt.AlignCenter)  # Align the canvas to the center of the window

        # Button toolbar
        toolbar_layout = QVBoxLayout()
        layout.addLayout(toolbar_layout)

        # Choose Color button with icon
        self.color_button = QPushButton()
        self.color_button.setIcon(QIcon("/home/douhan/Documents/scripts/doodle/icons/color_picker.png"))
        self.color_button.setIconSize(QSize(64, 64))
        self.color_button.setFixedSize(84, 84)
        self.color_button.clicked.connect(self.choose_color)
        toolbar_layout.addWidget(self.color_button)

        # Eraser Mode button with icon
        self.erase_button = QPushButton()
        self.erase_button.setIcon(QIcon("/home/douhan/Documents/scripts/doodle/icons/eraser.png"))
        self.erase_button.setIconSize(QSize(64, 64))
        self.erase_button.setFixedSize(84, 84)
        self.erase_button.clicked.connect(self.toggle_eraser_mode)
        toolbar_layout.addWidget(self.erase_button)

        # Add stretch to move buttons to the top
        toolbar_layout.addStretch()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def toggle_eraser_mode(self):
        self.eraser_mode = not self.eraser_mode

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            painter = QPainter(self.canvas)
            painter.setPen(QPen(Qt.white if self.eraser_mode else self.pen_color, self.pen_width, Qt.SolidLine))
            painter.drawLine(self.last_pos, event.pos())
            painter.end()
            self.last_pos = event.pos()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.canvas)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            clipboard = QApplication.clipboard()
            clipboard.setImage(self.canvas)
            QCoreApplication.quit()

def center_window(window):
    screen = QDesktopWidget().screenGeometry()
    window_geometry = window.frameGeometry()
    x = (screen.width() - window_geometry.width()) // 2
    y = (screen.height() - window_geometry.height()) // 2
    window.move(x, y)

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    canvas = DoodleCanvas()
    window.setCentralWidget(canvas)
    window.setWindowTitle("Douhan's Doodling Script")
    window.resize(1200, 900)  # Set initial window size
    center_window(window)  # Center the window on the screen
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
