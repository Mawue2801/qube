import os
import sys
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import numpy as np
import subprocess

# Add the root directory of your project to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

from database import DatabaseManager

class QuizCoach:
    def __init__(self):
        self.performance_data = {
            'rounds': {}
        }

    def update_performance(self, round_number, subject, correctness):
        # Initialize round data if it doesn't exist
        if round_number not in self.performance_data['rounds']:
            self.performance_data['rounds'][round_number] = {}

        # Initialize subject data if it doesn't exist for the round
        if subject not in self.performance_data['rounds'][round_number]:
            self.performance_data['rounds'][round_number][subject] = {
                'total': 0,
                'correct': 0,
                'incorrect': 0
            }

        # Update the correctness based on the input
        self.performance_data['rounds'][round_number][subject]['total'] += 1
        if correctness == 'correct':
            self.performance_data['rounds'][round_number][subject]['correct'] += 1
        elif correctness == 'incorrect':
            self.performance_data['rounds'][round_number][subject]['incorrect'] += 1
        else:
            raise ValueError(f"Unknown correctness type: {correctness}")

    def initialize_subjects(self):
        for round_number in range(1, 6):  # Since we have 5 rounds (1 to 5)
            if round_number not in self.performance_data['rounds']:
                self.performance_data['rounds'][round_number] = {}
            
            for subject in ['Chemistry', 'Physics', 'Math', 'Biology']:
                if subject not in self.performance_data['rounds'][round_number]:
                    self.performance_data['rounds'][round_number][subject] = {
                        'total': 0,
                        'correct': 0,
                        'incorrect': 0
                    }

    def update_user_performance_from_data(self, username, performance_data):
        def get_round_totals(round_number):
            round_totals = {
                'Math': {'total': 0, 'correct': 0},
                'Physics': {'total': 0, 'correct': 0},
                'Biology': {'total': 0, 'correct': 0},
                'Chemistry': {'total': 0, 'correct': 0}
            }
            
            if round_number in performance_data['rounds']:
                for subject in round_totals:
                    if subject in performance_data['rounds'][round_number]:
                        round_totals[subject]['total'] = performance_data['rounds'][round_number][subject]['total']
                        round_totals[subject]['correct'] = performance_data['rounds'][round_number][subject]['correct']
            
            return round_totals
        
        # Initialize variables to accumulate totals
        total_round_1 = get_round_totals(1)
        total_round_2 = get_round_totals(2)
        total_round_3 = get_round_totals(3)
        total_round_4 = get_round_totals(4)
        total_round_5 = get_round_totals(5)
        
        db_manager = DatabaseManager()

        # Call enter_user_performance with accumulated totals
        db_manager.enter_user_performance(
            username=username,
            round_1_total=sum(total_round_1[subject]['total'] for subject in total_round_1),
            round_1_correct=sum(total_round_1[subject]['correct'] for subject in total_round_1),
            round_2_total=sum(total_round_2[subject]['total'] for subject in total_round_2),
            round_2_correct=sum(total_round_2[subject]['correct'] for subject in total_round_2),
            round_3_total=sum(total_round_3[subject]['total'] for subject in total_round_3),
            round_3_correct=sum(total_round_3[subject]['correct'] for subject in total_round_3),
            round_4_total=sum(total_round_4[subject]['total'] for subject in total_round_4),
            round_4_correct=sum(total_round_4[subject]['correct'] for subject in total_round_4),
            round_5_total=sum(total_round_5[subject]['total'] for subject in total_round_5),
            round_5_correct=sum(total_round_5[subject]['correct'] for subject in total_round_5),
            math_total=(
                total_round_1['Math']['total'] + 
                total_round_2['Math']['total'] + 
                total_round_3['Math']['total'] +
                total_round_4['Math']['total'] + 
                total_round_5['Math']['total']
            ),
            math_correct=(
                total_round_1['Math']['correct'] + 
                total_round_2['Math']['correct'] + 
                total_round_3['Math']['correct'] +
                total_round_4['Math']['correct'] + 
                total_round_5['Math']['correct']
            ),
            physics_total=(
                total_round_1['Physics']['total'] + 
                total_round_2['Physics']['total'] + 
                total_round_3['Physics']['total'] +
                total_round_4['Physics']['total'] + 
                total_round_5['Physics']['total']
            ),
            physics_correct=(
                total_round_1['Physics']['correct'] + 
                total_round_2['Physics']['correct'] + 
                total_round_3['Physics']['correct'] +
                total_round_4['Physics']['correct'] + 
                total_round_5['Physics']['correct']
            ),
            biology_total=(
                total_round_1['Biology']['total'] + 
                total_round_2['Biology']['total'] + 
                total_round_3['Biology']['total'] +
                total_round_4['Biology']['total'] + 
                total_round_5['Biology']['total']
            ),
            biology_correct=(
                total_round_1['Biology']['correct'] + 
                total_round_2['Biology']['correct'] + 
                total_round_3['Biology']['correct'] +
                total_round_4['Biology']['correct'] + 
                total_round_5['Biology']['correct']
            ),
            chemistry_total=(
                total_round_1['Chemistry']['total'] + 
                total_round_2['Chemistry']['total'] + 
                total_round_3['Chemistry']['total'] +
                total_round_4['Chemistry']['total'] + 
                total_round_5['Chemistry']['total']
            ),
            chemistry_correct=(
                total_round_1['Chemistry']['correct'] + 
                total_round_2['Chemistry']['correct'] + 
                total_round_3['Chemistry']['correct'] +
                total_round_4['Chemistry']['correct'] + 
                total_round_5['Chemistry']['correct']
            ),
            win_streak=None
        )

    def create_performance_report(self, date, stage, year, schools, performance_data, logo_path, font_path_regular, font_path_bold):
        # Register the Poppins fonts
        pdfmetrics.registerFont(TTFont('Poppins', font_path_regular))
        pdfmetrics.registerFont(TTFont('Poppins-Bold', font_path_bold))

        # Create bar charts using matplotlib
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))  # Adjust figsize to better fit aspect ratio

        # Extract rounds and subjects
        rounds = list(performance_data['rounds'].keys())
        subjects = list(performance_data['rounds'][1].keys())

        # Correct vs Incorrect chart for each round
        correct_counts = [sum(performance_data['rounds'][round][subject]['correct'] for subject in subjects) for round in rounds]
        incorrect_counts = [sum(performance_data['rounds'][round][subject]['incorrect'] for subject in subjects) for round in rounds]

        bar_width = 0.35
        r1 = np.arange(len(rounds))
        r2 = [x + bar_width for x in r1]

        ax.bar(r1, correct_counts, color='#6a0dad', width=bar_width, edgecolor='grey', label='Correct')
        ax.bar(r2, incorrect_counts, color='#d8bfd8', width=bar_width, edgecolor='grey', label='Incorrect')

        ax.set_xlabel('Rounds', fontweight='bold')
        ax.set_xticks([r + bar_width / 2 for r in range(len(rounds))])
        ax.set_xticklabels([f'Round {round}' for round in rounds])
        ax.legend()
        ax.set_title('Correct vs Incorrect per Round')
        plt.tight_layout()

        # Save the plot to a BytesIO object without extra white space
        plot_image = io.BytesIO()
        plt.savefig(plot_image, format='png', bbox_inches='tight')
        plot_image.seek(0)

        # Create PDF using reportlab
        pdf_file = 'performance_report.pdf'
        c = canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4

        # Draw the logo while maintaining its aspect ratio
        logo = ImageReader(logo_path)
        logo_width, logo_height = logo.getSize()
        aspect_ratio = logo_width / logo_height
        logo_display_width = 70
        logo_display_height = logo_display_width / aspect_ratio
        c.drawImage(logo, width - logo_display_width - 80, height - logo_display_height - 60, width=logo_display_width, height=logo_display_height, preserveAspectRatio=True, mask='auto')

        # Title and metadata
        c.setFont("Poppins-Bold", 40)
        c.drawString(50, height - 110, "report")

        c.setFont("Poppins", 12)
        c.drawString(50, height - 190, f"Date: {date}")
        c.drawString(50, height - 210, f"Stage: {stage}")
        c.drawString(50, height - 230, f"Year: {year}")
        c.drawString(50, height - 250, f"Schools: {schools}")

        # Embed the plots
        c.drawImage(ImageReader(plot_image), 50, height - 550, width=500, height=250)

        # Table for performance data
        c.setFont("Poppins-Bold", 12)
        c.drawString(50, height - 580, "Subject Performance per Round:")
        
        # Prepare the table data
        data = [["Round"] + subjects]
        for round in rounds:
            row = [f'Round {round}']
            for subject in subjects:
                correct = performance_data['rounds'][round][subject]['correct']
                incorrect = performance_data['rounds'][round][subject]['incorrect']
                row.append(f"{correct} ({incorrect})")
            data.append(row)

        # Draw the table with horizontal lines and no vertical lines
        x_offset = 50
        y_offset = height - 610
        row_height = 20
        col_widths = [(width - 2 * x_offset) // len(data[0])] * len(data[0])  # Adjust column widths to cover the width of the page with margins

        for row_idx, row in enumerate(data):
            c.setFont("Poppins-Bold" if row_idx == 0 else "Poppins", 12)
            for i, cell in enumerate(row):
                c.drawString(x_offset + sum(col_widths[:i]), y_offset, str(cell))
            y_offset -= row_height
            c.line(x_offset, y_offset + row_height - 5, x_offset + sum(col_widths), y_offset + row_height - 5)  # Add horizontal line

        # Add explanation of the table structure below the table
        y_offset -= row_height - 20
        c.setFont("Poppins", 8)
        c.drawString(x_offset, y_offset, "Note: The values in each cell represent the number of correctly answered questions.")
        y_offset -= row_height - 10
        c.drawString(x_offset, y_offset, "The number in parentheses represents the number of incorrect answers.")

        # Add footer
        c.setFont("Poppins", 10)
        c.drawString(50, 30, "© 2024")
        c.drawRightString(width - 50, 30, "Generated by Qube")

        # Save the PDF
        c.save()

        # Open the PDF using default viewer based on platform
        if os.name == 'nt':  # For Windows
            os.startfile(pdf_file)
        elif os.name == 'posix':  # For Linux and macOS
            subprocess.Popen(['xdg-open', pdf_file])
        else:
            raise RuntimeError("Unsupported operating system")

    def print_performance_data(self):
        print(self.performance_data)

# # Example usage:
# quiz_coach = QuizCoach()

# quiz_coach.update_performance(1, 'Chemistry', 'correct')
# quiz_coach.update_performance(1, 'Physics', 'incorrect')
# quiz_coach.update_performance(2, 'Math', 'correct')
# quiz_coach.update_performance(5, 'Biology', 'incorrect')

# # Ensure all subjects have data in all rounds up to the current round
# quiz_coach.initialize_subjects()

# # Example of using update_user_performance_from_data:
# # Assuming `database_instance` and `username` are defined elsewhere
# # quiz_coach.update_user_performance_from_data(database_instance, username)

# # Print the updated performance data
# quiz_coach.print_performance_data()