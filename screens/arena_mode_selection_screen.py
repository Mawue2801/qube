import os
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QDesktopWidget, QPushButton, QDialog, QProgressBar,QSpacerItem
from PyQt5.QtGui import QPixmap, QIcon, QFont, QCursor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer

class LoadingWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)  # Remove title bar
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(200, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Loading Quizzes...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar {color: #ffffff; background-color: #6A0DAD; border-style: none; border-radius: 10px; padding: 2px;} QProgressBar::chunk {background-color: #B82FED;}")
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def start(self):
        # Center the loading widget
        screen_geometry = QDesktopWidget().screenGeometry(-1)
        x = int((screen_geometry.width() - self.width()) / 2)
        y = int((screen_geometry.height() - self.height()) / 2)
        self.move(x, y)

        self.show()

    def finish(self):
        self.close()

class ArenaModeSelectionScreen(QWidget):
    switch_to_dashboard = pyqtSignal(str)
    switch_to_arena_settings = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()

        self.username = username

        layout = QVBoxLayout()
        self.card_widget = QFrame()
        self.card_widget.setStyleSheet("background-color: white; border: none;")

        # Construct absolute path to the assets folder in the root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        assets_dir = os.path.join(root_dir, "assets")

        # Construct absolute paths to the images for the buttons
        single_player_image_path = os.path.join(assets_dir, "images/single_player.png")
        multi_player_image_path = os.path.join(assets_dir, "images/multi_player.png")
        logo_path = os.path.join(assets_dir, "images/logo.png")
        back_arrow_path = os.path.join(assets_dir, "images/back.png")

        # Set card width and height
        screen_size = QDesktopWidget().screenGeometry(-1)
        card_width = int(screen_size.width() // 1.5)
        card_height = int(screen_size.height() // 1.5)
        self.card_widget.setFixedSize(card_width, card_height)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)  # Align buttons to center

        # Create layout for back button
        back_layout = QHBoxLayout()
        back_layout.setAlignment(Qt.AlignLeft)  # Align to the left

        # Add back button
        back_button = QPushButton()
        back_button.setIcon(QIcon(back_arrow_path))
        back_button.setIconSize(QSize(30, 30))  # Adjust icon size
        back_button.setStyleSheet("QPushButton { border: none; background-color: transparent; margin-left: 1px; margin-top: 20px; }")

        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.clicked.connect(self.go_back)

        back_layout.addWidget(back_button)

        card_layout.addLayout(back_layout)

        # Add label for "Select Arena Mode"
        select_arena_label = QLabel("Select Arena Mode")
        select_arena_label.setAlignment(Qt.AlignCenter)
        select_arena_label.setStyleSheet("font-size: 20px; margin-top: 30px; margin-bottom: 50px; ")

        card_layout.addWidget(select_arena_label)

        # Create layout for buttons and labels
        button_layout = QHBoxLayout()

        # Add single player button with image and label
        single_player_button_layout = QVBoxLayout()
        single_player_button = QPushButton()
        single_player_button.setIcon(QIcon(single_player_image_path))
        single_player_button.setIconSize(QSize(150, 150))  # Adjust icon size
        single_player_button.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 10px;
                background-color: #330145;
                padding: 80px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #4C0167;
            }
        """)
        single_player_button.clicked.connect(self.start_single_player)

        single_player_label = QLabel("Single Player")
        single_player_label.setAlignment(Qt.AlignCenter)
        single_player_label.setStyleSheet("font-size: 20px;")
        single_player_button_layout.addWidget(single_player_button)
        single_player_button_layout.addWidget(single_player_label)
        single_player_button_layout.setAlignment(Qt.AlignCenter)

        # Add multiplayer button with image and label
        multi_player_button_layout = QVBoxLayout()
        multi_player_button = QPushButton()
        multi_player_button.setIcon(QIcon(multi_player_image_path))
        multi_player_button.setIconSize(QSize(150, 150))  # Adjust icon size
        multi_player_button.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 10px;
                background-color: #330145;
                padding: 80px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #4C0167;
            }
        """)
        multi_player_button.setEnabled(False) 
        multi_player_button.clicked.connect(self.start_multi_player)

        multi_player_label = QLabel("MultiPlayer")
        multi_player_label.setAlignment(Qt.AlignCenter)
        multi_player_label.setStyleSheet("font-size: 20px;")
        multi_player_button_layout.addWidget(multi_player_button)
        multi_player_button_layout.addWidget(multi_player_label)
        multi_player_button_layout.setAlignment(Qt.AlignCenter)

        button_layout.addSpacerItem(QSpacerItem(250, 20))
        button_layout.addLayout(single_player_button_layout)
        button_layout.addLayout(multi_player_button_layout)
        button_layout.addSpacerItem(QSpacerItem(250, 20))

        card_layout.addLayout(button_layout)

        # Add "Powered by" label and logo at the bottom
        powered_by_layout = QHBoxLayout()
        powered_by_label = QLabel("Powered by")
        powered_by_logo = QLabel()
        powered_by_pixmap = QPixmap(logo_path)
        powered_by_logo.setPixmap(powered_by_pixmap.scaledToWidth(35, Qt.SmoothTransformation))

        powered_by_layout.addWidget(powered_by_label)
        powered_by_layout.addWidget(powered_by_logo)
        powered_by_layout.setAlignment(Qt.AlignCenter)
        powered_by_layout.setSpacing(10)

        card_layout.addSpacing(80) 

        card_layout.addLayout(powered_by_layout)

        self.card_widget.setLayout(card_layout)

        # Center card in the window
        self.center_card()

        layout.addWidget(self.card_widget)
        self.setLayout(layout)

        # Create loading widget
        self.loading_widget = LoadingWidget()

    def center_card(self):
        screen_size = QDesktopWidget().screenGeometry(-1)
        window_width = screen_size.width()
        window_height = screen_size.height()
        window_x = (window_width - self.card_widget.width()) // 2
        window_y = (window_height - self.card_widget.height()) // 2
        # Position the widget at the center of the window
        self.card_widget.move(window_x, window_y)

    def go_back(self):
        self.switch_to_dashboard.emit(self.username)

    def start_single_player(self):
        # Show loading widget while processing
        self.loading_widget.start()

        # Emulate some work being done
        QTimer.singleShot(1000, self.finish_loading)  # Simulating some process taking time

    def finish_loading(self):
        # Emit signal to switch to single player screen
        self.switch_to_arena_settings.emit(self.username)
        self.loading_widget.finish()
        

    def start_multi_player(self):
        # Add your logic here to start multi player mode
        pass

# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    username = 'j.doe'
    arena_screen = ArenaModeSelectionScreen(username)
    arena_screen.show()
    sys.exit(app.exec_())
