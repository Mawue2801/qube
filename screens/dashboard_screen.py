from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QDesktopWidget, QGridLayout, QTableWidget, QTableWidgetItem, QSizePolicy, QPushButton, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import os
import sys

# Add the root directory of your project to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

from database import DatabaseManager

class DashboardScreen(QWidget):
    switch_to_arena_mode_selection = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username

        db_manager = DatabaseManager()
        user_info = db_manager.get_user_info(username)
        user_performance = db_manager.get_user_performance(username)
        user_scores = db_manager.get_user_scores(username)

        layout = QVBoxLayout()
        self.card_widget = QFrame()
        self.card_widget.setStyleSheet("background-color: white; border: none;")

        # Construct absolute path to the assets folder in the root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        assets_dir = os.path.join(root_dir, "assets")

        # Construct absolute path to the logo file
        logo_path = os.path.join(assets_dir, "images/logo.png")

        self.round_scores = [user_scores.get(f"round_{i+1}", 0) for i in range(5)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_progress_bars)
        self.timer.start(5)

        # Set card width and height
        screen_size = QDesktopWidget().screenGeometry(-1)
        card_width = int(screen_size.width() // 1.5)
        card_height = int(screen_size.height() // 1.5)
        self.card_widget.setFixedSize(card_width, card_height)

        card_layout = QVBoxLayout()

        # Create layout for image, button, greeting label, and text
        header_layout = QHBoxLayout()

        # Add greeting label
        greeting_label = QLabel(f"Hi, {user_info['first_name']} {user_info['last_name']}")
        greeting_label.setAlignment(Qt.AlignLeft)
        greeting_label.setStyleSheet("QLabel { font-size: 18px; padding: 10px; margin-left: 20px; margin-top: 20px; margin-bottom: 20px; }")

        # Load and display the image
        image_label = QLabel()
        image_pixmap = QPixmap(os.path.join(assets_dir, "images/fire.png"))
        image_label.setPixmap(image_pixmap.scaledToWidth(40, Qt.SmoothTransformation))

        # Replace the code for creating the avatar label with a button
        start_quiz_button = QPushButton("Start Quiz")
        start_quiz_button.setStyleSheet("QPushButton { background-color: #330145; color: white; border-radius: 5px; border: none; font-weight: bold; font-size: 15px; padding:15px; margin-right: 20px; margin-top: 20px; margin-bottom: 20px;} QPushButton:hover { background-color: #4C0167; }")
        start_quiz_button.clicked.connect(self.start_quiz)

        # Create label for win streaks
        win_streaks_label = QLabel(f"{user_performance['win_streak']} win streaks")
        win_streaks_label.setStyleSheet("color: black; font-size: 15px; font-weight: bold; margin-right: 5px;")

        # Add widgets to the layout
        header_layout.addWidget(greeting_label)
        header_layout.addStretch()
        header_layout.addWidget(image_label)
        header_layout.addWidget(win_streaks_label)
        header_layout.addWidget(start_quiz_button)
        
        card_layout.addLayout(header_layout)

        # Create a grid layout for the dashboard elements
        grid_layout = QGridLayout()

        # Create labels for subjects
        subjects = ["Math", "Chemistry", "Physics", "Biology"]
        for i, subject in enumerate(subjects):
            label = QLabel(f"{subject}<br><span style='font-size: 40px; font-weight: bold; margin-top: 50px;'>{round(user_scores[subject.lower()],2)}</span>")
            label.setFixedSize(280, 120)  # Set the same size for all subject cards
            label.setStyleSheet("background-color: #F5DAFE; border: 0px solid gray; border-radius: 10px; font-size: 15px; padding: 10px;")
            label.setAlignment(Qt.AlignCenter)
            label.setTextFormat(Qt.RichText)
            grid_layout.addWidget(label, 0, i, 1, 1)

        # Create a table for scores
        scores_label = QLabel("Rounds")
        scores_label.setStyleSheet("font-size: 20px; padding: 10px;")

        main_layout = QVBoxLayout()

        for i in range(5):
            row_layout = QVBoxLayout()

            round_label = QLabel(f"Round {i+1}")
            round_label.setStyleSheet("font-size: 15px; padding: 5px; border: none; background-color: transparent;")
            row_layout.addWidget(round_label)

            progress_layout = QHBoxLayout()

            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 5px;
                    background-color: #e0e0e0;
                }
                QProgressBar::chunk {
                    background-color: #8e44ad;
                    border-radius: 5px;
                }
            """)
            progress_bar.setFixedHeight(20)
            progress_bar.setTextVisible(False)
            progress_bar.setObjectName(f"progress_bar_{i}")
            progress_layout.addWidget(progress_bar)

            score_label = QLabel(f"{round(self.round_scores[i],2)}")
            score_label.setStyleSheet("font-size: 15px; padding: 5px; border: none; background-color: transparent;")
            progress_layout.addWidget(score_label)

            row_layout.addLayout(progress_layout)

            main_layout.addLayout(row_layout)

        card_frame = QFrame()
        card_frame.setLayout(main_layout)
        card_frame.setStyleSheet("""
            QFrame {
                border: none;
                border-radius: 10px;
                background-color: transparent;
                padding:0px;
            }
        """)
        card_frame.setFixedWidth(280)

        scores_layout = QVBoxLayout()
        scores_layout.addWidget(scores_label)
        scores_layout.addWidget(card_frame)
        scores_frame = QFrame()
        scores_frame.setLayout(scores_layout)
        scores_frame.setFixedWidth(280)

        # Create a label for history
        history_label = QLabel("History")
        history_label.setStyleSheet("font-size: 20px; padding: 10px;")
        history_content = QLabel("No data available")
        history_content.setStyleSheet("background-color: white; border: 1px solid gray; border-radius: 5px; font-size: 15px; padding: 160px;")
        history_content.setAlignment(Qt.AlignCenter)
        
        history_layout = QVBoxLayout()
        history_layout.addWidget(history_label)
        history_layout.addWidget(history_content)
        history_frame = QFrame()
        history_frame.setLayout(history_layout)

        # Add scores and history to the grid
        grid_layout.addWidget(scores_frame, 1, 0, 1, 1)
        grid_layout.addWidget(history_frame, 1, 1, 1, 3)

        # Set vertical and horizontal spacing
        grid_layout.setVerticalSpacing(0)
        grid_layout.setHorizontalSpacing(10)

        card_layout.addLayout(grid_layout)

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

        card_layout.addLayout(powered_by_layout)

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

    def start_quiz(self):
        self.switch_to_arena_mode_selection.emit(self.username)

    def animate_progress_bars(self):
        # Method to animate progress bars
        animation_in_progress = False  # Flag to track if animation is in progress
        for i in range(5):
            progress_bar = self.findChild(QProgressBar, f"progress_bar_{i}")
            if progress_bar is not None:
                target_value = round(self.round_scores[i] * 100 ) # Round the target value to the nearest integer
                current_value = progress_bar.value()  # Get the current value of the progress bar
                # print(f"Current Value: {current_value}, Target Value: {target_value}")
                if current_value < target_value:
                    animation_in_progress = True
                    progress_bar.setValue(current_value + 1)
        
        # If animation is not in progress (all progress bars reached their target values), stop the timer
        if not animation_in_progress:
            self.timer.stop()

# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    import os
    import sys

    # Add the root directory of your project to the Python path
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # root_dir = os.path.dirname(script_dir)
    # sys.path.append(root_dir)

    # from database import DatabaseManager

    # db_manager = DatabaseManager()

    # db_manager.update_user_performance(username="j.doe", round_1=0.88, round_2=0.05, round_3=0.9, round_4=0.225, round_5=0.55)

    app = QApplication(sys.argv)
    # Assume first_name and last_name are obtained from the login screen
    username = "j.doe"
    
    dashboard_screen = DashboardScreen(username)
    dashboard_screen.show()
    sys.exit(app.exec_())
