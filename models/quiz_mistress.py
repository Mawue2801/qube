import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class QuizMistress:
    def __init__(self, quiz_data):
        self.quiz_data = quiz_data
        self.current_question_index = 0
        self.current_set_index = 0
        self.score = {school: 0 for school in quiz_data['schools']}

        # Load pre-trained sentence transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    def get_stage(self):
        current_stage = self.quiz_data['stage']
        return current_stage
    
    def get_year(self):
        year = self.quiz_data['year']
        return year
    
    def get_schools(self):
        schools = self.quiz_data['schools']
        return schools
    
    def get_round(self):
        current_round = self.quiz_data['round']
        return current_round

    def read_preamble(self):
        current_set = self.quiz_data['sets'][self.current_set_index]
        return current_set['preamble']
    
    def read_subject(self):
        current_set = self.quiz_data['sets'][self.current_set_index]
        return current_set['subject']
    
    def read_opening_statement(self):
        opening_statement = self.quiz_data['opening_statement']
        return opening_statement
    
    def read_closing_statement(self):
        closing_statement = self.quiz_data['closing_statement']
        return closing_statement

    def ask_question(self):
        current_set = self.quiz_data['sets'][self.current_set_index]
        if self.current_question_index < len(current_set['questions_and_responses']):
            question = current_set['questions_and_responses'][self.current_question_index]
            return question
        else:
            return None

    def validate_response(self, attempted_response, expected_response):
        return attempted_response.strip().lower() == expected_response.strip().lower()

    def score_response(self, attempted_response, school, expected_response):
        response_quality = self.evaluate_response_quality(attempted_response, expected_response)
        self.score[school] += response_quality
        return response_quality

    def calculate_similarity(self, expected_answer, provided_answer):
        # Generate embeddings for both sentences
        expected_embedding = self.model.encode([expected_answer])[0]
        provided_embedding = self.model.encode([provided_answer])[0]
        
        # Compute cosine similarity
        similarity = cosine_similarity([expected_embedding], [provided_embedding])[0][0]
        
        return similarity

    def evaluate_response_quality(self, attempted_response, expected_response):
        current_round = self.quiz_data['round']
        if current_round == 1:
            similarity_score = self.calculate_similarity(expected_response.lower(), attempted_response.lower())
            threshold = 0.7
            if similarity_score >  0.7:
                score = 3
            else:
                score = 0
        elif current_round == 4:
            if expected_response.lower() in attempted_response.lower():
                score = 2
            else:
                score = -1
        return int(score)

    def determine_time_limit(self):
        current_set = self.quiz_data['sets'][self.current_set_index]
        return current_set['time_limit']

    def validate_bonus(self, school, attempted_response):
        current_set = self.quiz_data['sets'][self.current_set_index]
        question = current_set['questions_and_responses'][self.current_question_index]
        if question['bonus_attempt']['school'] == school:
            expected_response = question['expected_response']
            bonus_score = self.evaluate_response_quality(attempted_response, expected_response)
            question['bonus_attempt']['score'] = bonus_score
            self.score[school] += bonus_score

    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index >= len(self.quiz_data['sets'][self.current_set_index]['questions_and_responses']):
            self.current_question_index = 0
            self.current_set_index += 1
            if self.current_set_index >= len(self.quiz_data['sets']):
                return False
        return True