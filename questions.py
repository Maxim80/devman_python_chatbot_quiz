import os
import random


class NoMoreQuestions(Exception):
    """Исключение, которое выбрасывается, когда словать с вопросами пуст."""
    pass


class Questions():
    """
    Класс для работы с базов вопросов для викторины, которая представляет из
    себя словарь, где ключь вопрос, значение ответ на него.
    """
    def __init__(self, path_to_questions='questions.txt'):
        """Инициализация словаря с вопросами и ответами к ним."""
        self.questions_and_answers = self._upload_questions(path_to_questions)

    def _question_and_answer_normalize(self, text: str) -> str:
        """Выделяет из текста тело вопроса/ответа."""
        index = text.index(':')
        return text[index+1:].strip('\n')

    def _answer_normalize(self, answer: str) -> str:
        """
        Нормализует ответ пользователя, до точки или скобок, убирает лишние символы.
        """
        answer = answer.strip(' .').lower()
        index = 0
        for symbol in answer:
            if symbol == '(' and symbol == '.':
                break
            index +=1
        return answer[:index]

    def _upload_questions(self, path_to_questions: str) -> dict:
        """Загружает вопросы и ответы к ним из текстового файла."""
        questions = {}
        with open(path_to_questions, 'r', encoding='koi8-r') as f:
            text = f.read()
        text_lines = text.split('\n\n')
        for index, value in enumerate(text_lines):
            if 'Ответ:' in value:
                question = self._question_and_answer_normalize(text_lines[index-1])
                answer = self._question_and_answer_normalize(value)
                questions.update({question: answer})
        return questions

    def get_question(self) -> str:
        """Возвращает вопрос, выбранный в случайном порядке."""
        questions = list(self.questions_and_answers.keys())
        if not questions:
            raise NoMoreQuestions
        else:
            return random.choice(questions)

    def delete_question(self, question):
        """Удаляет вопрос."""
        self.questions_and_answers.pop(question)

    def get_correct_answer(self, question: str):
        """Возвращает ответ на вопрос."""
        return self.questions_and_answers[question]

    def is_answer_correct(self, question: str, answer: str) -> bool:
        "Проверяет правильность ответа на вопрос."
        correct_answer = self.questions_and_answers[question]
        correct_answer = self._answer_normalize(correct_answer)
        answer = self._answer_normalize(answer)
        if answer in correct_answer:
            self.delete_question(question)
            return True
        else:
            return False
