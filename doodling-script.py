import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QColorDialog, QDesktopWidget, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QClipboard, QImage, QPen, QIcon
from PyQt5.QtCore import Qt, QSize, QCoreApplication, QRect, QPoint

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
        self.select_mode = False
        self.selection_rect = None
        self.selection_active = False
        self.selection_start = None
        self.moving_selection = False
        self.selected_area_image = None
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
        self.color_button.setIcon(QIcon("/home/douhan/Documents/scripts/douhan-doodling-script/icons/color_picker.png"))
        self.color_button.setIconSize(QSize(64, 64))
        self.color_button.setFixedSize(QSize(84, 84))
        self.color_button.clicked.connect(self.choose_color)
        toolbar_layout.addWidget(self.color_button)

        # Color preset buttons with icons
        color_icons = {
            Qt.red: "/home/douhan/Documents/scripts/douhan-doodling-script/icons/red.png",
            Qt.green: "/home/douhan/Documents/scripts/douhan-doodling-script/icons/green.png",
            Qt.blue: "/home/douhan/Documents/scripts/douhan-doodling-script/icons/blue.png",
            Qt.black: "/home/douhan/Documents/scripts/douhan-doodling-script/icons/black.png"
        }
        for color, icon_path in color_icons.items():
            color_button = QPushButton()
            color_button.setIcon(QIcon(icon_path))
            color_button.setIconSize(QSize(64, 64))
            color_button.setFixedSize(QSize(84, 84))
            color_button.clicked.connect(lambda _, col=color: self.set_color(col))
            toolbar_layout.addWidget(color_button)

        # Eraser Mode button with icon
        self.erase_button = QPushButton()
        self.erase_button.setIcon(QIcon("/home/douhan/Documents/scripts/douhan-doodling-script/icons/eraser.png"))
        self.erase_button.setIconSize(QSize(64, 64))
        self.erase_button.setFixedSize(QSize(84, 84))
        self.erase_button.clicked.connect(self.toggle_eraser_mode)
        toolbar_layout.addWidget(self.erase_button)

        # Select Mode button with icon
        self.select_button = QPushButton()
        self.select_button.setIcon(QIcon("/home/douhan/Documents/scripts/douhan-doodling-script/icons/selection-tool.png"))
        self.select_button.setIconSize(QSize(64, 64))
        self.select_button.setFixedSize(QSize(84, 84))
        self.select_button.clicked.connect(self.toggle_select_mode)
        toolbar_layout.addWidget(self.select_button)

        # Add stretch to move buttons to the top
        toolbar_layout.addStretch()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def set_color(self, color):
        self.pen_color = color
        self.eraser_mode = False
        self.select_mode = False

    def toggle_eraser_mode(self):
        self.eraser_mode = not self.eraser_mode
        self.select_mode = False

    def toggle_select_mode(self):
        self.select_mode = not self.select_mode
        self.eraser_mode = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.select_mode:
                if self.selection_rect and self.selection_rect.contains(event.pos()):
                    self.moving_selection = True
                    self.selection_start = event.pos()
                else:
                    self.selection_rect = QRect(event.pos(), QSize())
                    self.selection_active = True
                    self.moving_selection = False
            else:
                self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.select_mode:
                if self.moving_selection and self.selection_rect:
                    offset = event.pos() - self.selection_start
                    self.selection_rect.translate(offset)
                    self.selection_start = event.pos()
                    self.update()
                elif self.selection_active:
                    self.selection_rect.setSize(QSize(event.pos().x() - self.selection_rect.left(), event.pos().y() - self.selection_rect.top()))
                    self.update()
            else:
                painter = QPainter(self.canvas)
                painter.setPen(QPen(Qt.white if self.eraser_mode else self.pen_color, self.pen_width, Qt.SolidLine))
                painter.drawLine(self.last_pos, event.pos())
                painter.end()
                self.last_pos = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):
        if self.select_mode:
            if self.selection_active:
                self.selection_active = False
                self.selected_area_image = self.canvas.copy(self.selection_rect)
                # Clear the selected area on the canvas
                painter = QPainter(self.canvas)
                painter.fillRect(self.selection_rect, Qt.white)
                painter.end()
            elif self.moving_selection:
                self.moving_selection = False
                # Draw the moved selection at the new location
                painter = QPainter(self.canvas)
                painter.drawImage(self.selection_rect.topLeft(), self.selected_area_image)
                painter.end()
                self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.canvas)
        if self.select_mode and self.selection_rect:
            painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
            painter.drawRect(self.selection_rect)
            if self.selected_area_image:
                painter.drawImage(self.selection_rect.topLeft(), self.selected_area_image)

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
