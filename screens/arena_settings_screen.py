import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QDesktopWidget, QPushButton,  QScrollArea, QDialog, QProgressBar, QFileDialog, QCheckBox, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QThread, pyqtSignal
from PIL import Image
from zipfile import ZipFile


# Add the root directory of your project to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)
from models.quiz_bank import QuizBank

class DownloadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, item, assets_dir):
        super().__init__()
        self.item = item
        self.assets_dir = assets_dir

    def run(self):
        file_name = self.item['file_name']
        output_path = os.path.join(self.assets_dir, f"data/{file_name}")
        extract_path = os.path.join(self.assets_dir, f"data")

        QuizBank.download_file(self.item['file_id'], output_path)

        with ZipFile(output_path, 'r') as f:
            #extract in current directory
            f.extractall(extract_path)
        
        os.remove(output_path)

        csv_path = os.path.join(self.assets_dir, "data/quiz_store.csv")
        QuizBank.append_to_local_csv(self.item, csv_path)
        self.finished.emit()

class SelectSchoolsDialog(QDialog):
    def __init__(self, item, assets_dir):
        super().__init__()

        # Construct absolute path to logo.png
        logo_path = os.path.join(assets_dir, "images/logo.png")

        self.setWindowTitle("Select Schools")

        # Set window icon
        if os.path.exists(logo_path):
            window_icon = QIcon(logo_path)
            self.setWindowIcon(window_icon)
        else:
            print(f"Logo file not found at: {logo_path}")

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.selected_schools = []
        self.image_path = None
        
        # Create layout
        layout = QVBoxLayout()
        
        # Instruction label
        label = QLabel("Select two schools:")
        layout.addWidget(label)

        schools = item['schools'].split(' vs. ')
        
        # School options
        self.school_checkboxes = [QCheckBox(f"{schools[0]}"), QCheckBox(f"{schools[1]}"), QCheckBox(f"{schools[2]}")]
        for checkbox in self.school_checkboxes:
            layout.addWidget(checkbox)
        
        # Select image button
        self.image_path = None
        select_image_button = QPushButton("Select Image (Optional)")
        select_image_button.clicked.connect(self.select_image)
        layout.addWidget(select_image_button)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Proceed button
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.proceed)
        button_layout.addWidget(proceed_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Add button layout to the main layout
        layout.addLayout(button_layout)
        
        # Set the dialog layout
        self.setLayout(layout)
    
    def select_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_path:
            self.image_path = file_path

    def proceed(self):
        selected_schools = [checkbox.text() for checkbox in self.school_checkboxes if checkbox.isChecked()]
        
        if len(selected_schools) != 2:
            QMessageBox.warning(self, "Error", "Please select exactly two schools.")
            return
        
        # print(f"Selected schools: {selected_schools}")

        self.selected_schools = selected_schools
        

        self.accept()

class LoadingWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)  # Remove title bar
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(200, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Setting up Arena...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { 
                color: #ffffff; 
                background-color: #6A0DAD; 
                border-style: none; 
                border-radius: 10px; 
                padding: 2px; 
            } 
            QProgressBar::chunk { 
                background-color: #B82FED; 
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

class ArenaSettingsScreen(QWidget):
    switch_to_arena_mode_selection = pyqtSignal(str)
    switch_to_arena = pyqtSignal(str,str,list,list,str)

    def __init__(self, username):
        super().__init__()

        # Construct absolute path to the assets folder in the root directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.script_dir)
        self.assets_dir = os.path.join(self.root_dir, "assets")

        self.selected_schools = []
        self.uploaded_image_path = None

        self.username = username
        self.local_data = []
        self.items = self.load_data()

        layout = QVBoxLayout()
        self.card_widget = QFrame()
        self.card_widget.setStyleSheet("background-color: white; border: none;")

        # Construct absolute paths to the images for the buttons
        back_arrow_path = os.path.join(self.assets_dir, "images/back.png")
        logo_path = os.path.join(self.assets_dir, "images/logo.png")

        # Set card width and height
        screen_size = QDesktopWidget().screenGeometry(-1)
        card_width = int(screen_size.width() // 1.5)
        card_height = int(screen_size.height() // 1.5)
        self.card_widget.setFixedSize(card_width, card_height)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)  # Align buttons to center

        # Create layout for buttons and labels
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 20, 0)  # Add right margin for spacing

        # Add back button
        back_button = QPushButton()
        back_button.setIcon(QIcon(back_arrow_path))
        back_button.setIconSize(QSize(30, 30))  # Adjust icon size
        back_button.setStyleSheet("QPushButton { border: none; background-color: transparent; margin-left: 1px; margin-top: 20px; }")

        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.clicked.connect(self.go_back)

        button_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # Add load data button
        load_data_button = QPushButton("Load Data")
        load_data_button.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                border-radius: 10px;
                background-color: #330145;
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4C0167;
            }
        """)
        load_data_button.clicked.connect(self.load_from_store)

        button_layout.addWidget(load_data_button, alignment=Qt.AlignRight)

        card_layout.addLayout(button_layout)

        # Add label for "Arena Settings"
        select_arena_label = QLabel("Arena Settings")
        select_arena_label.setAlignment(Qt.AlignCenter)
        select_arena_label.setStyleSheet("font-size: 20px; margin-top: 30px; margin-bottom: 50px; ")

        card_layout.addWidget(select_arena_label)

        # Create a scroll area to contain the card widgets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow scroll area to resize widget
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #f0f0f0; border: none; }"
                                       "QScrollBar:vertical { border: none; background: transparent; width: 4px; margin: 0px; }"
                                       "QScrollBar::handle:vertical { background: #888; min-height: 20px; border-radius: 5px; }"
                                       "QScrollBar::handle:vertical:hover { background: #555; }"
                                       "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }"
                                       "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }")
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_layout.setContentsMargins(20, 0, 20, 0)  # Adjust top and bottom margins
        self.scroll_area_layout.setSpacing(20)  # Add spacing between card widgets
        self.scroll_area_widget.setLayout(self.scroll_area_layout)

        # If items are empty, display a message
        if not self.items:
            no_data_label = QLabel("No data available")
            no_data_label.setStyleSheet("font-size: 18px; color: #666666;")
            no_data_label.setAlignment(Qt.AlignCenter)
            self.scroll_area_layout.addWidget(no_data_label)
        else:
            # Add card widgets for each item
            for item in self.items:
                card_widget = self.create_card_widget(item)
                self.scroll_area_layout.addWidget(card_widget)

        self.scroll_area.setWidget(self.scroll_area_widget)

        card_layout.addWidget(self.scroll_area)

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

        card_layout.addSpacing(120)

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

    def go_back(self):
        self.switch_to_arena_mode_selection.emit(self.username)

    def create_card_widget(self, item):
        # Create a card widget for the item
        card_widget = QFrame()
        card_widget.setStyleSheet("background-color: #f0f0f0; border: none; border-radius: 5px;")  # Removed border style
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)  # Add margins
        card_widget.setLayout(card_layout)

        # Extract information from the file_name to generate the primary label text
        file_name = item['file_name']

        # Extract the year from the last four characters of the first part split by '.'
        year = file_name.split('.')[0][-4:]

        # Extract the contest from 'Contest' till the year
        contest = file_name.split('.')[0].split('Contest')[-1][0:-4]

        # Extract the stage and day from the remaining part
        stage_day = file_name.split('.')[0].split('Contest')[0]
        stage_index = stage_day.index('Day')
        stage = stage_day[:stage_index]
        day = stage_day[stage_index + 3:]

        primary_text = f"{stage} Day {day} Contest {contest} {year}"

        # Add primary label
        primary_label = QLabel(primary_text)
        primary_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Add secondary label
        secondary_label = QLabel(item['schools'])
        secondary_label.setStyleSheet("font-size: 14px; color: #666666;")

        # Add start button
        start_button = QPushButton("Start")
        start_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #28a745;
                border-radius: 5px;
                background-color: #28a745;
                color: white;
                font-size: 14px;
                padding: 5px 10px;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        start_button.clicked.connect(lambda: self.open_dialog(item))

        # Add download button
        download_button = QPushButton("Download")
        download_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #007bff;
                border-radius: 5px;
                color: white;
                font-size: 14px;
                padding: 5px 10px;
            }
            QPushButton:enabled {
                background-color: #007bff;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border: 1px solid #cccccc;
            }
            QPushButton:hover:enabled {
                background-color: #0056b3;
            }
        """)

        # Check if item details are present in local data
        if item in self.local_data:
            download_button.setEnabled(False)  # Disable download button if item details are present in local data
            download_button.setText("Downloaded")

        download_button.clicked.connect(lambda: self.download_item(item, download_button))

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Add stretchable space to push buttons to the right
        button_layout.addWidget(start_button)
        button_layout.addWidget(download_button)

        # Add primary label, secondary label, and buttons to a vertical layout
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(primary_label)
        vertical_layout.addWidget(secondary_label)

        # Create a horizontal layout for the labels and buttons
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(vertical_layout)  # Add labels
        horizontal_layout.addLayout(button_layout)  # Add buttons

        # Add the horizontal layout to the card layout
        card_layout.addLayout(horizontal_layout)

        return card_widget
    
    def open_dialog(self, item):
        dialog = SelectSchoolsDialog(item, self.assets_dir)
        if dialog.exec_():
            self.school_blank_template = os.path.join(self.assets_dir, "images/school_blank_template.png")
            
            self.selected_schools = dialog.selected_schools
            self.uploaded_image_path = dialog.image_path
            output_path = os.path.join(self.assets_dir, "images/temp_school.png")

            if self.uploaded_image_path:
                # print(f"Selected image: {self.uploaded_image_path}")
                self.resize_and_merge_images(self.school_blank_template, self.uploaded_image_path, output_path)
            else:
                # print("No image selected")
                default_logo = os.path.join(self.assets_dir, "images/logo.png")
                self.resize_and_merge_images(self.school_blank_template, default_logo, output_path)

            self.start_arena(item)

        else:
            print("Dialog rejected")
    
    def resize_and_merge_images(self,template_path, image_path, output_path):
        # Open the template and the image to be resized
        template = Image.open(template_path).convert('RGBA')
        image = Image.open(image_path).convert('RGBA')

        # Get dimensions of the template
        template_width, template_height = template.size

        # Resize the image to fit within the template dimensions, preserving the aspect ratio
        image.thumbnail((template_width, template_height), Image.LANCZOS)

        # Calculate the position to place the resized image at the center of the template
        image_width, image_height = image.size
        x = (template_width - image_width) // 2
        y = (template_height - image_height) // 2

        # Create a copy of the template to paste the image onto
        combined = Image.new('RGBA', template.size)
        combined.paste(template, (0, 0))
        combined.paste(image, (x, y), image)

        # Save the final image
        combined.save(output_path)

    def start_arena(self, item):
        # Show the loading widget
        self.loading_widget = LoadingWidget(self)
        self.loading_widget.show()

        # Simulate loading process
        QTimer.singleShot(2000, lambda: self.go_to_arena(item))  # Delay to simulate loading time

    def go_to_arena(self, item):
        # Hide the loading widget
        selected_schools = [school.upper() for school in self.selected_schools]
        available_schools = [school.upper() for school in item['schools'].split(' vs. ')]
        # print(available_schools)
        uploaded_image_path = self.uploaded_image_path
        # print(selected_schools)
        self.loading_widget.hide()
        self.switch_to_arena.emit(self.username, item['file_name'],  available_schools, selected_schools, uploaded_image_path)  # Emit signal to switch to arena with file_id
        
    def download_item(self, item, button):
        # Handle download action for the item
        # print("Downloading:", item['file_name'])

        # Update button text to "Downloading..."
        button.setText("Downloading...")
        button.setEnabled(False)

        # Start the download in a separate thread
        self.download_thread = DownloadThread(item, self.assets_dir)
        self.download_thread.finished.connect(lambda: self.on_download_finished(button))
        self.download_thread.start()

    def on_download_finished(self, button):
        # Update button text to "Downloaded" and disable the button
        button.setText("Downloaded")
        button.setEnabled(False)

    def load_data(self):
        try:
            online_data = QuizBank.load_store_info()
        except Exception as e:
            print(f"An error occurred while loading online data: {e}")
            online_data = []

        try:
            csv_path = os.path.join(self.assets_dir, "data/quiz_store.csv")
            self.local_data = QuizBank.read_local_csv(csv_path)
        except Exception as e:
            print(f"An error occurred while reading local CSV data: {e}")
            self.local_data = []

        # Combine online and local data
        all_data = online_data + self.local_data

        # Remove duplicates
        unique_data = []
        seen_ids = set()
        for item in all_data:
            if item['file_id'] not in seen_ids:
                unique_data.append(item)
                seen_ids.add(item['file_id'])

        return unique_data

    def load_from_store(self):
        # Your existing implementation to load data
        self.items = self.load_data()
        # After loading data, recreate the card widgets and update the scroll area
        self.update_scroll_area()

    def update_scroll_area(self):
        # Clear the current content of the scroll area
        scroll_layout = self.scroll_area_widget.layout()
        if scroll_layout:
            while scroll_layout.count():
                item = scroll_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # If items are empty, display a message
        if not self.items:
            no_data_label = QLabel("No data available")
            no_data_label.setStyleSheet("font-size: 18px; color: #666666;")
            no_data_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(no_data_label)
        else:
            # Add card widgets for each item
            for item in self.items:
                card_widget = self.create_card_widget(item)
                scroll_layout.addWidget(card_widget)

        # Refresh the scroll area
        self.scroll_area_widget.setLayout(scroll_layout)


# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    username = 'j.doe'
    arena_settings_screen = ArenaSettingsScreen(username)
    arena_settings_screen.show()
    sys.exit(app.exec_())
