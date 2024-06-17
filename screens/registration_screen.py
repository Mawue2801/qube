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

class RegistrationScreen(QWidget):
    switch_to_login = pyqtSignal()
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
        card_height = int(screen_size.height() * 0.6)
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

        # Add first name and last name labels and fields in the same row
        name_layout = QHBoxLayout()

        # First name layout
        first_name_layout = QVBoxLayout()
        first_name_label = QLabel("First Name")
        first_name_label.setAlignment(Qt.AlignLeft)
        first_name_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.first_name_edit = QLineEdit()
        # self.set_line_edit_style(self.first_name_edit)
        self.first_name_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 5px; padding: 10px; margin-bottom: 15px; margin-left: 15px;} QLineEdit:focus { border: 2px solid #330145; }")
        first_name_layout.addWidget(first_name_label)
        first_name_layout.addWidget(self.first_name_edit)

        # Last name layout
        last_name_layout = QVBoxLayout()
        last_name_label = QLabel("Last Name")
        last_name_label.setAlignment(Qt.AlignLeft)
        last_name_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.last_name_edit = QLineEdit()
        # self.set_line_edit_style(self.last_name_edit)
        self.last_name_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 5px; padding: 10px; margin-bottom: 15px; margin-right: 15px;} QLineEdit:focus { border: 2px solid #330145; }")
        last_name_layout.addWidget(last_name_label)
        last_name_layout.addWidget(self.last_name_edit)

        # Add first name and last name layouts to the name_layout
        name_layout.addLayout(first_name_layout)
        name_layout.addLayout(last_name_layout)

        # Add name_layout to the card_layout
        card_layout.addLayout(name_layout)



        # Add school label and field
        school_label = QLabel("School")
        school_label.setAlignment(Qt.AlignLeft)
        school_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.school_edit = QLineEdit()
        self.set_line_edit_style(self.school_edit)
        card_layout.addWidget(school_label)
        card_layout.addWidget(self.school_edit)

        # Add password label and field
        password_label = QLabel("Password")
        password_label.setAlignment(Qt.AlignLeft)
        password_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.set_line_edit_style(self.password_edit)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_edit)

        # Add confirm password label and field
        confirm_password_label = QLabel("Confirm Password")
        confirm_password_label.setAlignment(Qt.AlignLeft)
        confirm_password_label.setStyleSheet("QLabel { padding: 0px; margin-left: 10px; font-size: 15px; }")
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.set_line_edit_style(self.confirm_password_edit)
        card_layout.addWidget(confirm_password_label)
        card_layout.addWidget(self.confirm_password_edit)

        # Add register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("QPushButton { background-color: #330145; color: white; border-radius: 5px; border: none; font-weight: bold; font-size: 15px; padding:15px; margin-top: 30px; margin-bottom: 20px; margin-left: 15px; margin-right: 15px;}")
        card_layout.addWidget(self.register_button)

        self.register_button.clicked.connect(self.register_button_clicked)

        # Add "Back to login" text button
        back_to_login_layout = QHBoxLayout()
        back_to_login_layout.setSpacing(0)
        back_to_login_label = QLabel("Already have an account? ")
        back_to_login_button = QPushButton("Login")
        back_to_login_button.setStyleSheet(" QPushButton { background: transparent; color: blue; border: none; padding: 0; } QPushButton:hover { color: darkblue; }")
        back_to_login_button.clicked.connect(self.switch_to_login.emit)
        back_to_login_layout.addWidget(back_to_login_label)
        back_to_login_layout.addWidget(back_to_login_button)
        back_to_login_layout.setAlignment(Qt.AlignCenter)
        back_to_login_widget = QWidget()
        back_to_login_widget.setLayout(back_to_login_layout)
        card_layout.addWidget(back_to_login_widget)

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
        line_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 5px; padding: 10px; margin-bottom: 15px; margin-left: 15px; margin-right: 15px;} QLineEdit:focus { border: 2px solid #330145; }")

    def register_button_clicked(self):
        # Perform input validation here
        first_name = self.first_name_edit.text()
        last_name = self.last_name_edit.text()
        school = self.school_edit.text()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not first_name or not last_name or not school or not password or not confirm_password:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Warning", "Passwords do not match.")
            return

        # If input is valid, register the user
        db_manager = DatabaseManager()
        db_manager.register_user(first_name, last_name, school, password)
        db_manager.close()

        username = first_name.lower() + '_' + last_name.lower()

        # Emit signal with username
        self.switch_to_dashboard.emit(username)

        # Optionally, you can show a success message here
        # QMessageBox.information(self, "Success", "Registration successful. You can now log in.")


# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    registration_screen = RegistrationScreen()

    registration_screen.show()
    sys.exit(app.exec_())
