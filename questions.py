from config import PATH_TO_QUESTIONS_FILES
from typing import List
from exceptions import NoMoreQuestions
import os
import random


QuestionsAndAnswers = dict
Question = str
Answer = str


class QuestionsForQuiz:
    def __init__(self, questions_and_answers: QuestionsAndAnswers) -> None:
        self.questions_and_answers = questions_and_answers
    
    def _answer_normalize(self, answer: Answer) -> Answer:
        answer = answer.strip(' .').lower()
        index = 0
        for symbol in answer:
            if symbol == '(' and symbol == '.':
                break
            index +=1
        return answer[:index]
    
    def get_question(self) -> Question:
        questions: List[Question] = list(self.questions_and_answers.keys())
        if not questions:
            raise NoMoreQuestions
        else:
            return random.choice(questions)

    def get_answer(self, question: Question) -> Answer:
        return self.questions_and_answers[question]
    
    def delete_question(self, question: Question) -> Answer:
        return self.questions_and_answers.pop(question)
    
    def check_answer(self, question: Question, user_answer: Answer) -> bool:
        correct_answer = self.questions_and_answers[question]
        correct_answer = self._answer_normalize(correct_answer)
        user_answer = self._answer_normalize(user_answer)
        if user_answer in correct_answer:
            return True
        else:
            return False


def _reading_text_from_files(file_paths: str) -> str:
    result_text = ''
    for path in file_paths:
        with open(path, 'r', encoding='koi8-r') as file:
            text = file.read()
        result_text += text
    return result_text


def _load_questions_from_files(path_to_questions_files: str) -> QuestionsAndAnswers:
    questions = {}
    file_paths = [
        os.path.join(PATH_TO_QUESTIONS_FILES, file_name)
        for file_name in os.listdir(path_to_questions_files)
    ]
    row_text = _reading_text_from_files(file_paths)
    text_lines = row_text.split('\n\n')
    for index, value in enumerate(text_lines):
        if 'Вопрос' in value:
            question = value.split(':')[1].strip('\n')
            answer = text_lines[index+1].split(':')[1].strip('\n')
            questions.update({question: answer})
    return questions
 

def get_questions(path_to_questions_files: str=PATH_TO_QUESTIONS_FILES)-> QuestionsForQuiz:
    questions = _load_questions_from_files(path_to_questions_files)
    return QuestionsForQuiz(questions)
