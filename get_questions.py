import re
import os


def create_questions_and_answer_dict():
    regex_questions = r"(?<=Вопрос\D\d\:\n).*?(?=\nОтвет)|(?<=Вопрос\D\d\d:\n).*?(?=\nОтвет)" \
                      r"|(?<=Вопрос\D\d\d\d:\n).*?(?=\nОтвет)"
    regex_answers = r'(?<=Ответ:\n).*?(?=\n)'
    questions_and_answer = {}

    file_names = os.listdir(path=os.path.join('questions'))

    for file_name in file_names:
        with open(f'questions/{file_name}', 'r', encoding='KOI8-R')as file:
            file_text = file.read()

        questions = re.finditer(regex_questions, file_text, re.MULTILINE | re.DOTALL)
        answers = re.finditer(regex_answers, file_text, re.MULTILINE | re.DOTALL)

    for id_question, (question, answer) in enumerate(zip(questions, answers), start=1):

        questions_and_answer.update({id_question:
                                    {'question': question.group().replace('\n', ' '),
                                     'answer': answer.group()}})

    return questions_and_answer
