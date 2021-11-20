import qa_conf


class Conversions:
    @staticmethod
    def raw_to_dict(raw: str) -> dict:
        output: dict = {}

        newlineSep = conf.FileCodes.question_separators['nl']
        spaceSep = conf.FileCodes.question_separators['space']
        questionAnswerSep = conf.FileCodes.question_separators['qas']

        for line in raw.split('\n'):
            line = line.strip()
            if len(line) > 0:
                if questionAnswerSep in line:
                    q = line.split(questionAnswerSep)[0].strip()
                    a = line.replace(q, "", 1).replace(questionAnswerSep, '').strip()

                    if len(q) > 0 and len(a) > 0:
                        for c, ac in {spaceSep: ' ', newlineSep: '\n'}.items():
                            q = q.replace(c, ac); a = a.replace(c, ac)
                        q = q.strip(); a = a.strip()

                        if len(q) > 0 and len(a) > 0:
                            output[q] = a

        return output

    @staticmethod
    def convertToQuestionStr(question: str, answer: str):
        question = question.strip()
        answer = answer.strip()

        if not len(question) > 0 or not len(answer) > 0:
            return

        seps = conf.FileCodes.question_separators
        newlineSep = seps.get('nl')
        spaceSep = seps.get('space')
        QASep = seps.get('qas')

        question = question.replace(newlineSep, '').replace(spaceSep, '').strip()
        answer = answer.replace(newlineSep, '').replace(spaceSep, '').strip()

        if not len(question) > 0 or not len(answer) > 0:
            return

        # Replace
        question = question.replace('\n', newlineSep)
        question = question.replace(' ', spaceSep)
        answer = answer.replace('\n', newlineSep)
        answer = answer.replace(' ', spaceSep)

        question = question.strip()
        answer = answer.strip()

        # Concat
        output = f"{question}{QASep}{answer}"

        return output

    @staticmethod
    def dictToSaveStr(data: dict) -> str:
        output = ""
        for i in data:
            qa = Conversions.convertToQuestionStr(i, data[i])
            output += f"{qa}\n"

        return output
