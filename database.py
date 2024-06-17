from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import hashlib
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    school = Column(String)
    password = Column(String)
    performances = relationship("UserPerformance", back_populates="user")

class UserPerformance(Base):
    __tablename__ = 'user_performance'

    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'))
    user = relationship("User", back_populates="performances")

    # Questions and Correct Answers per Subject
    math_total = Column(Integer, default=0)
    math_correct = Column(Integer, default=0)
    physics_total = Column(Integer, default=0)
    physics_correct = Column(Integer, default=0)
    biology_total = Column(Integer, default=0)
    biology_correct = Column(Integer, default=0)
    chemistry_total = Column(Integer, default=0)
    chemistry_correct = Column(Integer, default=0)

    # Questions and Correct Answers per Round
    round_1_total = Column(Integer, default=0)
    round_1_correct = Column(Integer, default=0)
    round_2_total = Column(Integer, default=0)
    round_2_correct = Column(Integer, default=0)
    round_3_total = Column(Integer, default=0)
    round_3_correct = Column(Integer, default=0)
    round_4_total = Column(Integer, default=0)
    round_4_correct = Column(Integer, default=0)
    round_5_total = Column(Integer, default=0)
    round_5_correct = Column(Integer, default=0)

    # Win streak
    win_streak = Column(Integer, default=0)

class DatabaseManager:
    def __init__(self):
        self.db_file = '.user_data.db'
        self.engine = create_engine(f'sqlite:///{self.db_file}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.hide_db_file()

    def hide_db_file(self):
        if os.name == 'nt':  # Check if the OS is Windows
            import ctypes
            file_attribute_hidden = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(self.db_file, file_attribute_hidden)

    def generate_username(self, first_name, last_name):
        return first_name.lower() + '_' + last_name.lower()

    def register_user(self, first_name, last_name, school, password):
        # Generate username
        username = self.generate_username(first_name, last_name)

        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        new_user = User(first_name=first_name, last_name=last_name, username=username, school=school, password=hashed_password)
        self.session.add(new_user)

        # Create a new performance entry with all values set to 0
        new_performance = UserPerformance(username=username)
        self.session.add(new_performance)

        self.session.commit()

    def login_user(self, username, password):
        # Hash the input password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = self.session.query(User).filter_by(username=username, password=hashed_password).first()
        return user is not None

    def get_user_info(self, username):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            return {'first_name': user.first_name, 'last_name': user.last_name, 'school': user.school}
        else:
            return None

    def get_user_performance(self, username):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            performance = user.performances[0]  # Assuming each user has only one performance record
            if performance:
                return {
                    'math_total': performance.math_total,
                    'math_correct': performance.math_correct,
                    'physics_total': performance.physics_total,
                    'physics_correct': performance.physics_correct,
                    'biology_total': performance.biology_total,
                    'biology_correct': performance.biology_correct,
                    'chemistry_total': performance.chemistry_total,
                    'chemistry_correct': performance.chemistry_correct,
                    'round_1_total': performance.round_1_total,
                    'round_1_correct': performance.round_1_correct,
                    'round_2_total': performance.round_2_total,
                    'round_2_correct': performance.round_2_correct,
                    'round_3_total': performance.round_3_total,
                    'round_3_correct': performance.round_3_correct,
                    'round_4_total': performance.round_4_total,
                    'round_4_correct': performance.round_4_correct,
                    'round_5_total': performance.round_5_total,
                    'round_5_correct': performance.round_5_correct,
                    'win_streak': performance.win_streak
                }
        return None
    
    def enter_user_performance(self, username, math_total=None, math_correct=None,
                               physics_total=None, physics_correct=None,
                               biology_total=None, biology_correct=None,
                               chemistry_total=None, chemistry_correct=None,
                               round_1_total=None, round_1_correct=None,
                               round_2_total=None, round_2_correct=None,
                               round_3_total=None, round_3_correct=None,
                               round_4_total=None, round_4_correct=None,
                               round_5_total=None, round_5_correct=None,
                               win_streak=None):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            performance = user.performances[0]  # Assuming each user has only one performance record
            if performance:
                if math_total is not None and math_correct is not None:
                    performance.math_total += math_total
                    performance.math_correct += math_correct
                if physics_total is not None and physics_correct is not None:
                    performance.physics_total += physics_total
                    performance.physics_correct += physics_correct
                if biology_total is not None and biology_correct is not None:
                    performance.biology_total += biology_total
                    performance.biology_correct += biology_correct
                if chemistry_total is not None and chemistry_correct is not None:
                    performance.chemistry_total += chemistry_total
                    performance.chemistry_correct += chemistry_correct
                if round_1_total is not None and round_1_correct is not None:
                    performance.round_1_total += round_1_total
                    performance.round_1_correct += round_1_correct
                if round_2_total is not None and round_2_correct is not None:
                    performance.round_2_total += round_2_total
                    performance.round_2_correct += round_2_correct
                if round_3_total is not None and round_3_correct is not None:
                    performance.round_3_total += round_3_total
                    performance.round_3_correct += round_3_correct
                if round_4_total is not None and round_4_correct is not None:
                    performance.round_4_total += round_4_total
                    performance.round_4_correct += round_4_correct
                if round_5_total is not None and round_5_correct is not None:
                    performance.round_5_total += round_5_total
                    performance.round_5_correct += round_5_correct
                if win_streak is not None:
                    performance.win_streak = win_streak
                self.session.commit()

    def update_user_performance(self, username, subject_totals=None, subject_corrects=None, round_totals=None, round_corrects=None, win_streak=None):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            performance = user.performances[0]  # Assuming each user has only one performance record
            if performance:
                if subject_totals:
                    if 'math' in subject_totals:
                        performance.math_total = subject_totals['math']
                    if 'physics' in subject_totals:
                        performance.physics_total = subject_totals['physics']
                    if 'biology' in subject_totals:
                        performance.biology_total = subject_totals['biology']
                    if 'chemistry' in subject_totals:
                        performance.chemistry_total = subject_totals['chemistry']
                if subject_corrects:
                    if 'math' in subject_corrects:
                        performance.math_correct = subject_corrects['math']
                    if 'physics' in subject_corrects:
                        performance.physics_correct = subject_corrects['physics']
                    if 'biology' in subject_corrects:
                        performance.biology_correct = subject_corrects['biology']
                    if 'chemistry' in subject_corrects:
                        performance.chemistry_correct = subject_corrects['chemistry']
                if round_totals:
                    if 'round_1' in round_totals:
                        performance.round_1_total = round_totals['round_1']
                    if 'round_2' in round_totals:
                        performance.round_2_total = round_totals['round_2']
                    if 'round_3' in round_totals:
                        performance.round_3_total = round_totals['round_3']
                    if 'round_4' in round_totals:
                        performance.round_4_total = round_totals['round_4']
                    if 'round_5' in round_totals:
                        performance.round_5_total = round_totals['round_5']
                if round_corrects:
                    if 'round_1' in round_corrects:
                        performance.round_1_correct = round_corrects['round_1']
                    if 'round_2' in round_corrects:
                        performance.round_2_correct = round_corrects['round_2']
                    if 'round_3' in round_corrects:
                        performance.round_3_correct = round_corrects['round_3']
                    if 'round_4' in round_corrects:
                        performance.round_4_correct = round_corrects['round_4']
                    if 'round_5' in round_corrects:
                        performance.round_5_correct = round_corrects['round_5']
                if win_streak is not None:
                    performance.win_streak = win_streak
                self.session.commit()

    def calculate_score(self, correct, total):
        if total == 0:
            return 0.0
        return correct / total

    def get_user_scores(self, username):
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            performance = user.performances[0]  # Assuming each user has only one performance record
            if performance:
                scores = {
                    'math': self.calculate_score(performance.math_correct, performance.math_total),
                    'physics': self.calculate_score(performance.physics_correct, performance.physics_total),
                    'biology': self.calculate_score(performance.biology_correct, performance.biology_total),
                    'chemistry': self.calculate_score(performance.chemistry_correct, performance.chemistry_total),
                    'round_1': self.calculate_score(performance.round_1_correct, performance.round_1_total),
                    'round_2': self.calculate_score(performance.round_2_correct, performance.round_2_total),
                    'round_3': self.calculate_score(performance.round_3_correct, performance.round_3_total),
                    'round_4': self.calculate_score(performance.round_4_correct, performance.round_4_total),
                    'round_5': self.calculate_score(performance.round_5_correct, performance.round_5_total)
                }
                return scores
        return None

    def close(self):
        self.session.close()
