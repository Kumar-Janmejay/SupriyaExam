import json
import random
from typing import List, Dict, Optional

class QuestionLoader:
    def __init__(self):
        self.questions = []
        self.load_question_bank()
    
    def load_question_bank(self):
        """Load questions from multiple JSON files"""
        question_files = [
            'data/questions_db.json'  # This file would contain all 400+ questions in the required format,
           
        ]
        
        all_questions = []
        
        for file_path in question_files:
            try:
                # Since we have the data directly, we'll create the JSON structure
                questions_data = self.create_question_structure(file_path)
                all_questions.extend(questions_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        self.questions = all_questions
    
    def create_question_structure(self,file_path) -> List[Dict]:
        """Read questions from JSON filepath and return structured list."""
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            abs_path = os.path.join(base_dir, file_path.replace('/', os.sep))
            with open(abs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Support either a direct list or {"questions": [...]}
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("questions"), list):
                return data["questions"]

            print(f"Invalid question format in {file_path}. Expected list or {{'questions': [...]}}")
            return []
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def load_questions(self, shuffle: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Load and optionally shuffle questions"""
        questions = self.questions.copy()
        
        if shuffle:
            random.shuffle(questions)
        
        if limit:
            questions = questions[:limit]
        
        # Shuffle options for each question
        for question in questions:
            if shuffle:
                self.shuffle_question_options(question)
        
        return questions
    
    def shuffle_question_options(self, question: Dict):
        """Shuffle options while maintaining correct answer"""
        options = question['options']
        correct_index = question['correct']
        correct_answer = options[correct_index]
        
        # Create list of (option, is_correct) tuples
        option_tuples = [(opt, i == correct_index) for i, opt in enumerate(options)]
        
        # Shuffle the tuples
        random.shuffle(option_tuples)
        
        # Update question
        question['options'] = [opt for opt, _ in option_tuples]
        question['correct'] = next(i for i, (_, is_correct) in enumerate(option_tuples) if is_correct)
    
    def get_total_questions(self) -> int:
        """Get total number of questions"""
        return len(self.questions)
    
    def get_topics(self) -> List[str]:
        """Get list of unique topics"""
        return list(set(q['topic'] for q in self.questions))
    
    def get_questions_by_topic(self, topic: str) -> List[Dict]:
        """Get questions for a specific topic"""
        return [q for q in self.questions if q['topic'] == topic]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get questions by difficulty level"""
        return [q for q in self.questions if q['difficulty'] == difficulty]
