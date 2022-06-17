from questions import user_answer_check
import unittest


class TestUserAnswerCheck(unittest.TestCase):
    def test_correct_answer_one(self):
        cases = [
            'Нисколько',
            'нисколько',
            'нискоЛЬко',
            'Нисколько.',
            '  Нисколько ',
            'Нисколько (некие пояснения в скобках)',
        ]
        correct_answer = 'Нисколько (т.к. использовался неразменный пятак).'
        for case in cases:
            with self.subTest(case=case):
                is_user_answer_correctly = user_answer_check(
                    case, correct_answer
                )
                self.assertTrue(is_user_answer_correctly)

    def test_correct_answer_two(self):
        cases = [
            'Твой номер - шестнадцатый',
            'Твой номер - шестнадцатый.',
            'Твой номер шестнадцатый.',
            '"Твой номер шестнадцатый"',
        ]
        correct_answer = '"Твой номер - шестнадцатый".'
        for case in cases:
            with self.subTest(case=case):
                is_user_answer_correctly = user_answer_check(
                    case, correct_answer
                )
                self.assertTrue(is_user_answer_correctly)


if __name__ == '__main__':
    unittest.main()
