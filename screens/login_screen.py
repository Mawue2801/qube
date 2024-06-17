import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QDesktopWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import os
import sys

# Add the root directory of your project to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

from database import DatabaseManager

class LoginScreen(QWidget):
    # Define a signal for switching to the registration screen
    switch_to_registration = pyqtSignal()
    switch_to_dashboard = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.card_widget = QFrame()
        self.card_widget.setStyleSheet("background-color: white; border-radius: 10px;")

         # Construct absolute path to the assets folder in the root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        assets_dir = os.path.join(root_dir, "assets")

        # Construct absolute path to the logo file
        logo_path = os.path.join(assets_dir, "images/logo.png")

        # Set card width and height
        screen_size = QDesktopWidget().screenGeometry(-1)
        card_width = int(screen_size.width() * 0.2)
        card_height = int(screen_size.height() * 0.45)
        self.card_widget.setFixedSize(card_width, card_height)

        card_layout = QVBoxLayout()

        # Add logo to the top of the card
        self.logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        pixmap = pixmap.scaledToWidth(int(card_width * 0.2))  # Resize the pixmap to 20% of the card width
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("padding: 40px;")
        card_layout.addWidget(self.logo_label)

        # Add username label and field
        username_label = QLabel("Username")
        username_label.setAlignment(Qt.AlignLeft)
        username_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("firstname_lastname")
        self.set_line_edit_style(self.username_edit)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_edit)

        # Add password label and field
        password_label = QLabel("Password")
        password_label.setAlignment(Qt.AlignLeft)
        password_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.set_line_edit_style(self.password_edit)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_edit)

        # Add login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("QPushButton { background-color: #330145; color: white; border-radius: 5px; border: none; font-weight: bold; font-size: 15px; padding:15px; margin-top: 30px; margin-bottom: 20px; margin-left: 15px; margin-right: 15px;}")
        card_layout.addWidget(self.login_button)

        # Connect login_button_clicked function to login_button's clicked signal
        self.login_button.clicked.connect(self.login_button_clicked)

        # Add "Create one" text button
        create_account_layout = QHBoxLayout()
        create_account_layout.setSpacing(0)
        create_account_label = QLabel("Do not have an account? ")
        create_account_button = QPushButton("Create one")
        create_account_button.setStyleSheet(" QPushButton { background: transparent; color: blue; border: none; padding: 0; } QPushButton:hover { color: darkblue; }")
        create_account_button.clicked.connect(self.switch_to_registration.emit)
        create_account_layout.addWidget(create_account_label)
        create_account_layout.addWidget(create_account_button)
        create_account_layout.setAlignment(Qt.AlignCenter)
        create_account_widget = QWidget()
        create_account_widget.setLayout(create_account_layout)
        card_layout.addWidget(create_account_widget)

        self.card_widget.setLayout(card_layout)

        # Center card in the window
        self.center_card()

        layout.addWidget(self.card_widget)
        self.setLayout(layout)

    def center_card(self):
        screen_size = QDesktopWidget().screenGeometry(-1)
        window_width = screen_size.width()
        window_height = screen_size.height()
        window_x = (window_width - self.card_widget.width()) // 2
        window_y = (window_height - self.card_widget.height()) // 2
        self.card_widget.move(window_x, window_y)

    def set_line_edit_style(self, line_edit):
        line_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 7px; padding: 10px; margin-left: 15px; margin-right: 15px; margin-bottom: 15px; } QLineEdit:focus { border: 2px solid #330145; }")

    def login_button_clicked(self):
        # Retrieve username and password from input fields
        username = self.username_edit.text()
        password = self.password_edit.text()

        temp_username = username.split('_')
        username = temp_username[0].lower() + "_" + temp_username[1].lower()

        # Check if username and password are correct by calling login_user method from DatabaseManager
        db_manager = DatabaseManager()
        if db_manager.login_user(username, password):
            # Get user information
            user_info = db_manager.get_user_info(username)

            # Emit signal with username, first name, and last name
            self.switch_to_dashboard.emit(username.lower())
        else:
            # Login failed, display an error message
            QMessageBox.warning(self, "Warning", "Invalid username or password.")
        db_manager.close()

# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    login_screen = LoginScreen()
    login_screen.show()
    sys.exit(app.exec_())
