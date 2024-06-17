import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDesktopWidget, QLabel, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from screens.login_screen import LoginScreen
from screens.registration_screen import RegistrationScreen
from screens.dashboard_screen import DashboardScreen
from screens.arena_mode_selection_screen import ArenaModeSelectionScreen
from screens.arena_settings_screen import ArenaSettingsScreen
from screens.arena_screen import ArenaScreen
from PyQt5.QtCore import QT_VERSION_STR

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

class SplashScreen(QSplashScreen):
    def __init__(self, image_path, screen_size):
        pixmap = QPixmap(image_path)
        
        # Resize the image to half the width of the screen while maintaining aspect ratio
        scaled_pixmap = pixmap.scaledToWidth(screen_size.width() // 2, Qt.SmoothTransformation)
        
        super().__init__(scaled_pixmap, Qt.WindowStaysOnTopHint)
        
        # Center the splash screen on the screen
        self.setGeometry(
            (screen_size.width() - scaled_pixmap.width()) // 2,
            (screen_size.height() - scaled_pixmap.height()) // 2,
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.current_screen = None

        # Get the absolute path of the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct absolute path to the assets folder
        assets_dir = os.path.join(script_dir, "assets")

        # Construct absolute path to logo.png
        self.logo_path = os.path.join(assets_dir, "images/logo.png")

        self.login_screen = LoginScreen()
        self.registration_screen = RegistrationScreen()

        self.login_screen.switch_to_registration.connect(self.show_registration_screen)
        self.registration_screen.switch_to_login.connect(self.show_login_screen)
        self.login_screen.switch_to_dashboard.connect(self.show_dashboard)
        self.registration_screen.switch_to_dashboard.connect(self.show_dashboard)

        self.show_login_screen()

        # Set window size and position
        self.resize_and_center()

        # Set window icon
        self.set_window_icon(self.logo_path)

    def resize_and_center(self):
        screen_size = QDesktopWidget().screenGeometry(-1)
        window_width = screen_size.width() // 1.5
        window_height = screen_size.height() // 1.5
        window_x = (screen_size.width() - window_width) // 2
        window_y = (screen_size.height() - window_height) // 2
        self.setGeometry(int(window_x), int(window_y), int(window_width), int(window_height))

    def set_window_icon(self, icon_path):
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

    def switch_screen(self, screen):
        if self.current_screen:
            self.layout.removeWidget(self.current_screen)
            self.current_screen.setParent(None)
        self.current_screen = screen
        self.layout.addWidget(screen)
        self.layout.setAlignment(screen, Qt.AlignCenter)

    def show_login_screen(self):
        self.switch_screen(self.login_screen)

    def show_registration_screen(self):
        self.switch_screen(self.registration_screen)
    
    def show_dashboard(self, username):
        self.dashboard_screen = DashboardScreen(username)
        self.switch_screen(self.dashboard_screen)
        self.dashboard_screen.switch_to_arena_mode_selection.connect(self.show_arena_mode_selection_screen)
    
    def show_arena_mode_selection_screen(self, username):
        self.arena_mode_selection_screen = ArenaModeSelectionScreen(username)
        self.switch_screen(self.arena_mode_selection_screen)
        self.arena_mode_selection_screen.switch_to_dashboard.connect(self.show_dashboard)
        self.arena_mode_selection_screen.switch_to_arena_settings.connect(self.show_arena_settings_screen)

    def show_arena_settings_screen(self, username):
        self.arena_settings_screen = ArenaSettingsScreen(username)
        self.switch_screen(self.arena_settings_screen)
        self.arena_settings_screen.switch_to_arena_mode_selection.connect(self.show_arena_mode_selection_screen)
        self.arena_settings_screen.switch_to_arena.connect(self.show_arena_screen)
    
    def show_arena_screen(self, username, filename, available_schools, selected_schools, uploaded_image_path):
        self.arena_screen = ArenaScreen(username, filename, available_schools, selected_schools, uploaded_image_path)
        self.switch_screen(self.arena_screen)
        self.arena_screen.switch_to_dashboard.connect(self.show_dashboard)


if __name__ == "__main__":

    # ASCII art and color codes
    ascii_art = """
    \033[95m                
 _____ _____ _____ _____ 
|     |  |  | __  |   __|
|  |  |  |  | __ -|   __|
|__  _|_____|_____|_____|
   |__|                  
    \033[0m
    """
    app_name = "\033[95mSEE\033[0m"
    version = "\033[95mv1.0.0\033[0m"
    developer = "Samuel & Mawunyo"
    copyright_info = "© 2024 See. All rights reserved."
    license_info = "Licensed under the Apache-2.0 License."
    environment_info = f"Python {sys.version.split()[0]}, Qt {QT_VERSION_STR}"

    # Printing information with formatting
    print(ascii_art)
    print(f"{app_name} {version}")
    print(f"Developer: {developer}")
    print(f"{copyright_info}")
    print(f"{license_info}")
    print(f"Environment: {environment_info}")
    print("\n\033[95mInitializing application...\033[0m")

    app = QApplication(sys.argv)
    
    # Get the screen size
    screen_size = QDesktopWidget().screenGeometry(-1)
    
    # Construct absolute path to the splash screen image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    splash_image_path = os.path.join(assets_dir, "images/splash_screen.png")
    
    # Create and show the splash screen
    splash = SplashScreen(splash_image_path, screen_size)
    splash.show()
    
    # Create the main window
    window = MainWindow()
    
    # Set a timer to close the splash screen and show the main window
    QTimer.singleShot(3000, splash.close)
    QTimer.singleShot(3000, window.show)
    
    sys.exit(app.exec_())
