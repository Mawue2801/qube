import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QDesktopWidget, QPushButton, QComboBox, QTextEdit, QSpacerItem, QSizePolicy, QApplication, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QFont, QCursor, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QPointF, pyqtSlot
import sys
import numpy as np
import pyaudio
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import whisper
import torch
from TTS.tts.configs.vits_config import VitsConfig
from TTS.tts.models.vits import Vits
from TTS.utils.audio.numpy_transforms import save_wav
import json
import time
import datetime
import cv2
from scipy.io import wavfile
from datetime import datetime

# Add the root directory of your project to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

from widgets.waveform_widget import WaveformWidget
from widgets.custom_combo_widget import CustomComboBox
from models.quiz_mistress import QuizMistress
from models.quiz_coach import QuizCoach
from database import DatabaseManager

class ArenaScreen(QWidget):
    switch_to_dashboard = pyqtSignal(str)
    # speech_detected = pyqtSignal()
    hand_raised = pyqtSignal()

    def __init__(self, username, foldername, available_schools, selected_schools, uploaded_image_path):
        super().__init__()

        # self.speech_detected.connect(self.stop_timer_on_speech)
        self.hand_raised.connect(self.stop_timer_on_hand_raised)

        # Construct absolute path to the assets folder in the root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        assets_dir = os.path.join(root_dir, "assets")

        foldername = foldername.split('.')[0]

        # Directory path where your JSON files are located
        directory = os.path.join(assets_dir, f"data/{foldername}")

        # Initialize an empty list to store quiz data from each file
        self.quiz_data = []

        # Get a list of all JSON files in the directory
        json_files = [filename for filename in os.listdir(directory) if filename.endswith(".json")]

        # Sort the list of JSON files based on their numeric part (assuming format round_<number>.json)
        json_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

        # Loop through each sorted file in the directory
        for filename in json_files:
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                # Load JSON data from the file and append to quiz_data list
                self.quiz_data.append(json.load(file))

        self.current_round = 0

        # Initialize QuizMistress with quiz data
        self.quiz_mistress = QuizMistress(self.quiz_data[self.current_round])
        self.time_limit = 10
        self.quiz_timer = QTimer(self)
        self.previous_set_index = -1 # Track new set of questions to know when to read preamble

        self.is_speaking = False  # Initialize the is_speaking attribute
        self.volume_history = []  # List to store volume levels for averaging
        self.silence_duration = 0  # Track duration of silence
        self.continue_quiz = True

        self.current_stage = self.quiz_mistress.get_stage()
        self.current_subject = ''

        self.quiz_coach = QuizCoach()
        self.quiz_coach.initialize_subjects()

        self.username = username
        self.available_schools = available_schools
        print(self.available_schools)
        self.selected_schools = selected_schools
        self.uploaded_image_path = uploaded_image_path
        self.foldername = foldername

        db_manager = DatabaseManager()
        self.user_info = db_manager.get_user_info(username)

        student_config_path = os.path.join(assets_dir, "text_to_speech/config.json")
        student_model_path = os.path.join(assets_dir, "text_to_speech/coqui_vits.onnx")

        quizmistress_config_path = os.path.join(assets_dir, "text_to_speech/quizmistress config.json")
        quizmistress_model_path = os.path.join(assets_dir, "text_to_speech/quizmistress.onnx")

        self.student_config = VitsConfig()
        self.student_config.load_json(student_config_path)
        self.student_vits = Vits.init_from_config(self.student_config)
        self.student_vits.load_onnx(student_model_path)

        self.quizmistress_config = VitsConfig()
        self.quizmistress_config.load_json(quizmistress_config_path)
        self.quizmistress_config.model_args.speakers_file = os.path.join(assets_dir, "text_to_speech/quizmistress.pth")
        self.quizmistress_vits = Vits.init_from_config(self.quizmistress_config)
        self.quizmistress_vits.load_onnx(quizmistress_model_path)

        self.initUI()
        self.set_default_devices()

        # Use QTimer to delay the start of the quiz
        QTimer.singleShot(500, self.start_quiz)

    def initUI(self):
        layout = QVBoxLayout()
        self.card_widget = QFrame()
        self.card_widget.setStyleSheet("background-color: white; border: none;")

        # Construct absolute path to the assets folder in the root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        self.assets_dir = os.path.join(root_dir, "assets")

        # Construct absolute paths to the images for the buttons
        self.logo_path = os.path.join(self.assets_dir, "images/logo.png")

        # Set card width and height
        screen_size = QDesktopWidget().screenGeometry(-1)
        card_width = int(screen_size.width() // 1.5)
        card_height = int(screen_size.height() // 1.5)
        self.card_widget.setFixedSize(card_width, card_height)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)  # Align widgets to center

        # Create layout for quit button
        quit_layout = QHBoxLayout()
        quit_layout.setAlignment(Qt.AlignRight)  # Align to the right

        # Add quit button
        quit_button = QPushButton("Quit")
        quit_button.setStyleSheet("""
        QPushButton {
            color: #ff0000; /* Red color for text */
            border: 2px solid #ff0000; /* Red color for border */
            background-color: transparent; /* Transparent fill color */
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            margin: 20px;
        }
        
        QPushButton:hover {
            background-color: rgba(255, 0, 0, 0.8); /* Light red color on hover */
            color: #ffffff;
        }
        """)

        quit_button.clicked.connect(self.go_back)  # Quit the application

        quit_layout.addWidget(quit_button)

        card_layout.addLayout(quit_layout)

        # Add label for "Microphone" and dropdown
        mic_speaker_layout = QHBoxLayout()

        mic_label = QLabel("Microphone")
        self.mic_dropdown = CustomComboBox(self)

        speaker_label = QLabel("Speaker")
        self.speaker_dropdown = CustomComboBox(self)

        added_devices = set()  # Set to store already added devices
        for device in sd.query_devices():
            if device['name'] not in added_devices:
                if device['max_input_channels'] > 0:
                    self.mic_dropdown.addItem(device['name'])
                if device['max_output_channels'] > 0:
                    self.speaker_dropdown.addItem(device['name'])
                added_devices.add(device['name'])  # Add device name to the set

        self.mic_dropdown.currentTextChanged.connect(self.select_input_device)
        self.speaker_dropdown.currentTextChanged.connect(self.select_output_device)


        mic_speaker_layout.addWidget(mic_label)
        mic_speaker_layout.addWidget(self.mic_dropdown)
        mic_speaker_layout.addWidget(speaker_label)
        mic_speaker_layout.addWidget(self.speaker_dropdown)
        mic_speaker_layout.setAlignment(Qt.AlignCenter)

        card_layout.addLayout(mic_speaker_layout)

        # Add text row layout for Stage and Round
        text_row_layout = QHBoxLayout()
        self.stage_label = QLabel(f"Stage: {self.quiz_mistress.get_stage()}")
        self.stage_label.setStyleSheet("font-size: 15px; margin-top: 10px; margin-bottom: 10px; margin-right: 10px;")
        self.round_label = QLabel(f"Round: Round {self.quiz_mistress.get_round()}")
        self.round_label.setStyleSheet("font-size: 15px; margin-top: 10px; margin-bottom: 10px; margin-right: 10px;")
        text_row_layout.addWidget(self.stage_label)
        text_row_layout.addWidget(self.round_label)

        # Create a horizontal layout to center the text row layout
        center_text_row_layout = QHBoxLayout()
        center_text_row_layout.addStretch()  # Add stretchable space before the text row
        center_text_row_layout.addLayout(text_row_layout)  # Add the text row layout
        center_text_row_layout.addStretch()

        card_layout.addLayout(center_text_row_layout)

        # Add WaveformWidget
        self.waveform_widget = WaveformWidget()
        self.waveform_widget.audio_finished.connect(self.start_timer)
        self.waveform_widget.audio_finished.connect(self.detect_hand_raised)
        card_layout.addWidget(self.waveform_widget)  # Add the container widget to the card layout


        images = []
        names = []
        # images = ['BISHOP HERMAN COLLEGE', 'MPRAESO SHS', 'WESLEY GIRLS SHS']
        for school in self.available_schools:
            if school in self.selected_schools:
                images.append(os.path.join(self.assets_dir, f"data/{self.foldername}/logos/{school}.png"))
                names.append(school)
            else:
                images.append(self.uploaded_image_path)
                names.append(self.user_info['school'])

         # Add QLabel widgets with images and school names
        schools_layout = QHBoxLayout()

        # Load images and school names with fixed width
        for i in range(3):
            school_image = QPixmap(images[i]).scaledToWidth(75)
            school_label = QLabel(names[i].upper())
            school_label.setStyleSheet("border: 2px solid black;border-radius:12px; margin-top: 10px; margin-bottom: 10px; margin-left: 10px;")
            school_label.setPixmap(school_image)
            school_label.setAlignment(Qt.AlignLeft)
            school_label.setFixedWidth(88)
                    
            # Create a container widget to hold the image and label
            container_widget = QWidget()
            container_layout = QHBoxLayout()
            container_layout.addWidget(school_label)
            school_text = QLabel(names[i].upper())
            school_text.setAlignment(Qt.AlignLeft)
            container_layout.addWidget(school_text)


            school_text.setStyleSheet("border: none; margin-top: 40px; margin-right: 10px; font-weight: bold; font-size: 15px; color: white;")

             # Create QLabel for school points
            school_points = QLabel("")
            school_points.setAlignment(Qt.AlignLeft)
            school_points.setStyleSheet("border: none; font-size: 30px; color: white; margin-top: 30px; margin-right: 5px; font-weight: bold;")
            school_points.setFixedWidth(80)
            container_layout.addWidget(school_points)

            container_widget.setLayout(container_layout)
            
            # Set margins to create space for the border
            container_layout.setContentsMargins(2, 2, 2, 2)
            
            # Add outer border to the container widget
            container_widget.setStyleSheet("border: 2px solid black; border-radius: 5px; background-color:#4C0167;")
            
            schools_layout.addWidget(container_widget)


        card_layout.addLayout(schools_layout)

        # Add layout for text box and send button
        text_send_layout = QHBoxLayout()

        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("Transcribed text appear here")
        self.text_box.setStyleSheet("""
            QTextEdit {
                border: 2px solid grey;
                border-radius: 5px;
                font-size: 16px;
                color: black;
                min-height: 50px; /* Set minimum height for the text box */
                margin-bottom: 20px;
            }
            
            QTextEdit:focus {
                border: 2px solid purple;
            }
        """)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #4C0167;
                border-radius: 5px;
                background-color: #4C0167; /* Purple color */
                color: white;
                padding: 15px 20px;
                font-size: 16px;
                margin-bottom: 20px;
            }
            
            QPushButton:hover {
                background-color: #330145; /* Darker shade of purple on hover */
            }
        """)

        text_send_layout.addWidget(self.text_box)
        text_send_layout.addWidget(self.send_button)

        # self.text_box.textChanged.connect(self.stop_timer_on_typing)
        self.send_button.clicked.connect(self.submit_answer)

        card_layout.addLayout(text_send_layout)

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
        print("Quit application")
        # Show a confirmation dialog
        reply = QMessageBox.question(
            self, 
            'Quit Quiz', 
            'Are you sure you want to quit the quiz? Your progress will not be recorded.', 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.quiz_timer.stop()  # Stop the quiz timer if it's running

            # Stop recording if it's in progress
            if hasattr(self, 'stream') and self.stream.active:
                self.stream.stop()
                self.stream.close()

            self.continue_quiz = False

            # Emit the signal to switch to the dashboard
            self.switch_to_dashboard.emit(self.username)
        else:
            # User chose to continue with the quiz
            pass
        

    def set_default_devices(self):
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]

        input_info = sd.query_devices(default_input)
        output_info = sd.query_devices(default_output)

        if input_info:
            print("Default Input Device:", input_info['name'])
            self.mic_dropdown.setCurrentText(input_info['name'])
        else:
            print("Default Input Device: None")

        if output_info:
            print("Default Output Device:", output_info['name'])
            self.speaker_dropdown.setCurrentText(output_info['name'])
        else:
            print("Default Output Device: None")

    def select_input_device(self, name):
        input_device_id = None
        for idx, device in enumerate(sd.query_devices()):
            if device["name"] == name:
                input_device_id = idx
                break

        if input_device_id is not None:
            print("Selected input device:", name, "ID:", input_device_id)
            sd.default.device[0] = input_device_id
        else:
            print("Input device not found:", name)

    def select_output_device(self, name):
        output_device_id = None
        for idx, device in enumerate(sd.query_devices()):
            if device["name"] == name:
                output_device_id = idx
                break

        if output_device_id is not None:
            print("Selected output device:", name, "ID:", output_device_id)
            sd.default.device[1] = output_device_id
        else:
            print("Output device not found:", name)

    def record_audio(self):
        if self.continue_quiz:
            samplerate = 44100
            self.recorded_audio = []

            self.stream = sd.InputStream(samplerate=samplerate, channels=2, callback=self.audio_callback)
            self.stream.start()

            self.record_audio_timer = QTimer(self)
            self.record_audio_timer.start(100)

    def stop_recording(self):
        if not self.recorded_audio:
            print("No audio recorded.")
            return

        self.stream.stop()
        self.stream.close()
        self.record_audio_timer.stop()

        if len(self.recorded_audio) > 0:
            self.recorded_audio = np.concatenate(self.recorded_audio, axis=0)
            print("Recording complete.")
            self.silence_duration = 0
            self.process_audio()
        else:
            print("No audio recorded.")

    def audio_callback(self, indata, frames, time, status):
        if self.continue_quiz:
            self.recorded_audio.append(indata.copy())

            volume_norm = np.linalg.norm(indata) * 10
            self.volume_history.append(volume_norm)

            # Compute a simple moving average of the last 10 volume levels
            if len(self.volume_history) > 10:
                self.volume_history.pop(0)

            average_volume = np.mean(self.volume_history)
            self.is_speaking = average_volume > 2  # Adjust threshold as needed

            if self.is_speaking:
                # print("Speech detected")
                # self.speech_detected.emit()
                self.silence_duration = 0  # Reset silence duration if speaking
            else:
                self.silence_duration += frames / 44100.0  # Increment silence duration in seconds

            if self.silence_duration >= 3:  # Stop recording if silent for 3 seconds
                QTimer.singleShot(0, self.stop_recording)

    def process_audio(self):
        if hasattr(self, 'recorded_audio') and self.recorded_audio is not None:
            # Save recorded audio as a temporary .wav file
            temp_file_path = "temp_audio.wav"
            sf.write(temp_file_path, self.recorded_audio, 44100)

            self.text_box.setText("Transcribing...")

            QApplication.processEvents()

            # Transcribe the temporary .wav file
            model = whisper.load_model("tiny.en", device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
            result = model.transcribe(temp_file_path)

            self.text_box.setText(result["text"])

            # print("Transcription:", result["text"])

            # Delete the temporary .wav file
            os.remove(temp_file_path)
        else:
            print("No audio recorded.")

    def play_audio(self):
        if self.continue_quiz:
            temp_file_path = "temp_audio.wav"
            
            # Read the audio data from the file
            sample_rate, audio_data = wavfile.read(temp_file_path)
            
            # Play the audio data
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()
            # print("Playback complete.")
    
    def quizmistress_tts_call(self, text: str, output_path: str):
        text_inputs = np.asarray(
            self.quizmistress_vits.tokenizer.text_to_ids(text, language="en"),
            dtype=np.int64,
        )[None, :]
        audio = self.quizmistress_vits.inference_onnx(text_inputs,speaker_id=0)
        save_wav(wav=audio[0], path=output_path, sample_rate=22050)
        return output_path
    
    def student_tts_call(self, text: str, output_path: str):
        text_inputs = np.asarray(
            self.student_vits.tokenizer.text_to_ids(text, language="en"),
            dtype=np.int64,
        )[None, :]
        audio = self.student_vits.inference_onnx(text_inputs)
        save_wav(wav=audio[0], path=output_path, sample_rate=22050)
        return output_path
    
    def quizmistress_text_to_speech(self, response_text):
        if self.continue_quiz:
            temp_file_path = "temp_audio.wav"
            # Call the function and save the audio file to the specified path
            audio_file_path = self.quizmistress_tts_call(response_text, temp_file_path)

            # Output the path of the saved audio file
            # print(f"Audio file saved at: {audio_file_path}")

            self.waveform_widget.load_audio_file(audio_file_path)

            os.remove(temp_file_path)
        
    def contestant_text_to_speech(self, response_text):
        if self.continue_quiz:
            temp_file_path = "temp_audio.wav"
            # Call the function and save the audio file to the specified path
            audio_file_path = self.student_tts_call(response_text, temp_file_path)

            # Output the path of the saved audio file
            # print(f"Audio file saved at: {audio_file_path}")
            
            self.play_audio()

            os.remove(temp_file_path)

    def play_quizmistress_audio(self, response_text):
        if self.continue_quiz:
            temp_file_path = "temp_audio.wav"

            # Call the function and save the audio file to the specified path
            audio_file_path = self.quizmistress_tts_call(response_text, temp_file_path)

            # Output the path of the saved audio file
            # print(f"Audio file saved at: {audio_file_path}")
            
            self.play_audio()

            os.remove(temp_file_path)

    def stop_timer_on_speech(self):
        self.quiz_timer.stop()
        # self.speech_detected.disconnect()
    
    def stop_timer_on_hand_raised(self):
        self.quiz_timer.stop()

    def detect_hand_raised(self):
        if self.continue_quiz:
            current_question = self.quiz_mistress.ask_question()
            current_school = current_question['school']
            if current_school not in self.selected_schools:
                cap = cv2.VideoCapture(0)
                hand_cascade = cv2.CascadeClassifier(os.path.join(self.assets_dir, "palm.xml"))

                start_time = time.time()
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)

                    if len(hands) > 0:
                        # print("Hand detected!")
                        self.play_quizmistress_audio(f"Go ahead {self.user_info['school']}")
                        self.hand_raised.emit()
                        self.record_audio()
                        break

                    # Check timeout
                    if time.time() - start_time > self.time_limit:  # Timeout after 5 seconds
                        print("Timeout reached. No hand detected.")
                        break

                cap.release()
            else:
                self.hand_raised.emit()
                attempted_response = current_question['attempted_response']
                self.contestant_text_to_speech(attempted_response)
                self.text_box.setText(attempted_response)
                QApplication.processEvents()
                self.submit_answer()

    def start_quiz(self):
        # print("Start Quiz Running")
        opening_statement = self.quiz_mistress.read_opening_statement()
        self.play_quizmistress_audio(opening_statement)
        if self.quiz_mistress.read_preamble() and self.previous_set_index != self.quiz_mistress.current_set_index:
            preamble = self.quiz_mistress.read_preamble()
            self.play_quizmistress_audio(preamble)
            self.previous_set_index = self.quiz_mistress.current_set_index

        self.current_subject = self.quiz_mistress.read_subject()
        self.time_limit = self.quiz_mistress.determine_time_limit()

        current_question = self.quiz_mistress.ask_question()
        current_school = current_question['school']

        if current_school not in self.selected_schools:
            current_school = self.user_info['school']

        if current_question and self.continue_quiz:
            self.quizmistress_text_to_speech(current_school + '.' + current_question['question'])
        else:
            self.quiz_finished()

    def start_timer(self):
        if self.continue_quiz:
            # print("Starting timer")
            self.start_time = time.time()
            self.update_timer()
            self.quiz_timer.timeout.connect(self.update_timer)
            self.quiz_timer.start(1000)

    def update_timer(self):
        if self.continue_quiz:
            elapsed_time = int(time.time() - self.start_time)
            formatted_start_time = datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')
            # print("Starting timer at", formatted_start_time)
            self.time_left = max(0, self.time_limit - elapsed_time)
            # print(f'Time left: {self.time_left} seconds')

            if self.time_left <= 0:
                self.quiz_timer.stop()  
                print("Timer stopped")
                self.submit_answer()        
    
    # @pyqtSlot()
    # def stop_timer_on_typing(self):
    #     if not self.quiz_timer.isActive():
    #         return
    #     self.quiz_timer.stop()

    def submit_answer(self):
        if self.continue_quiz:
            # self.timer.stop()
            user_answer = self.text_box.toPlainText().strip().lower()
            current_question = self.quiz_mistress.ask_question()

            if current_question:
                expected_response = current_question['expected_response']
                school = current_question['school']
                score = self.quiz_mistress.score_response(user_answer, school, expected_response)
                
                if score == -1 or score == 0:
                    response_text = f"That's incorrect. The right answer is {expected_response}"

                    if school not in self.selected_schools:
                        # print("Scoring user")
                        self.quiz_coach.update_performance(self.quiz_mistress.get_round(), self.current_subject, 'incorrect')
                else:
                    response_text = "That's right"

                    if school not in self.selected_schools:
                        # print("Scoring user")
                        self.quiz_coach.update_performance(self.quiz_mistress.get_round(), self.current_subject, 'correct')

                self.play_quizmistress_audio(response_text)
                # QMessageBox.information(self, 'Score', f'Score for {school}: {score}')

            self.text_box.clear()

            if not self.quiz_mistress.next_question():
                self.quiz_finished()
            else:
                self.start_time = time.time()
                # print("Continue Quiz Running")
                if self.quiz_mistress.read_preamble() and self.previous_set_index != self.quiz_mistress.current_set_index:
                    preamble = self.quiz_mistress.read_preamble()
                    self.play_quizmistress_audio(preamble)
                    self.previous_set_index = self.quiz_mistress.current_set_index

                self.current_subject = self.quiz_mistress.read_subject()
                self.time_limit = self.quiz_mistress.determine_time_limit()

                current_question = self.quiz_mistress.ask_question()
                current_school = current_question['school']

                if current_school not in self.selected_schools:
                    current_school = self.user_info['school']

                if current_question:
                    self.quizmistress_text_to_speech(current_school + '.' + current_question['question'])

    def quiz_finished(self):
        # self.quiz_timer.stop()
        # self.send_button.setEnabled(False)
        total_scores = "\n".join([f"{school}: {score}" for school, score in self.quiz_mistress.score.items()])
        closing_statement = self.quiz_mistress.read_closing_statement()
        self.play_quizmistress_audio(closing_statement)
        self.quiz_coach.print_performance_data()
        self.quiz_coach.update_user_performance_from_data(self.username,self.quiz_coach.performance_data)
        QMessageBox.information(self, 'Scores', f'Round completed!\n\nScores:\n{total_scores}')
        len_of_quiz = len(self.quiz_data) - 1
        # print(self.current_round)
        # print(len_of_quiz)
        if self.current_round < len_of_quiz:
            self.current_round += 1
            # Initialize QuizMistress with quiz data
            self.quiz_mistress = QuizMistress(self.quiz_data[self.current_round])
            self.round_label.setText(f"Round: Round {self.quiz_mistress.get_round()}")
            QTimer.singleShot(500, self.start_quiz)
        else:
            print("Printing Report")
            # Get current date
            current_date = datetime.now()
            # Format the date as required
            date_string = current_date.strftime("%d/%m/%Y")
            
            stage = self.quiz_mistress.get_stage()
            year = self.quiz_mistress.get_year()
            schools = self.quiz_mistress.get_schools()

            font_path_regular = os.path.join(self.assets_dir, "fonts/Poppins-Regular.ttf")
            font_path_bold = os.path.join(self.assets_dir, "fonts/Poppins-Bold.ttf")

            self.quiz_coach.create_performance_report(date_string, stage, year, schools, self.quiz_coach.performance_data, self.logo_path, font_path_regular, font_path_bold)
            self.switch_to_dashboard.emit(self.username)


# Entry point
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    username = 'john_doe'
    filename = 'QuarterFinalsDay1Contest12023'
    available_schools = ['BISHOP HERMAN COLLEGE', 'MPRAESO SHS', 'WESLEY GIRLS SHS']
    selected_schools = ['BISHOP HERMAN COLLEGE', 'WESLEY GIRLS SHS']
    uploaded_image_path = 'C:/Users/HP/Desktop/Personal Projects/qube_ai/app/assets/images/temp_school.png'
    arena_screen = ArenaScreen(username, filename, available_schools, selected_schools, uploaded_image_path)
    arena_screen.show()
    sys.exit(app.exec_())
