# The following file defines the question standard
import traceback
from dataclasses import dataclass
import json, qa_tk
from typing import *


@dataclass
class Question:
    question: str
    answer: str
    type: int
    widget_requirement: int
    quid: str
    comments: List[str]


class StandardVariables:
    answer_key = 'answer'
    type_key = 'type'
    comments_key = 'comments'
    widget_key = 'widget'
    question_key = "question"

    question_type_map = {
        'r': {  # ID : (Code, Human Readable) [REVERSE]
            0: ('mcq', 'Multiple Choice Question'),
            1: ('nrm', 'Written Response Question'),
            2: ('t/f', 'True/False Question'),
        },
        'n': {  # Code: ID
            'mcq': 0,
            'nrm': 1,
            't/f': 2,
        }
    }

    widget_requirement_map = {
        'r': {  # ID: Widget
            0: qa_tk.Text,
            1: qa_tk.Entry
        },
        'n': {
            'extended_response': 0,
            'short_response': 1
        }
    }


class Functions:
    @staticmethod
    def str_to_questions(raw_json_data: str) -> tuple:
        try:
            js0 = json.loads(raw_json_data)
            qs = (*js0.keys(),)
        except Exception as E:
            print(f'QA Question Standardization - String To Questions - Failed to load data - {E}')

            js0 = {}
            qs = {}

        o0, failures = [], []

        for ind, q0 in enumerate(qs):
            q = js0[q0]
            try:
                assert StandardVariables.answer_key in q, f"Q{ind + 1}: No answer available"
                assert StandardVariables.type_key in q, f"Q{ind + 1}: No type data available"
                assert StandardVariables.widget_key in q, f"Q{ind + 1}: No answer widget data available"
                assert StandardVariables.question_key in q, f"Q{ind + 1}: No question ID available"

                o0.append(
                    Question(q0,
                             q[StandardVariables.answer_key],
                             q[StandardVariables.type_key],
                             q[StandardVariables.widget_key],
                             q[StandardVariables.question_key],
                             q[StandardVariables.comments_key] if isinstance(
                                 q.get(StandardVariables.comments_key), list
                             ) else [])
                )

            except Exception as E:
                failures.append(
                    (q0, str(E))
                )

        del qs, js0, raw_json_data

        return o0, failures

    @staticmethod
    def questions_to_json(ls: list, re_dict: bool = False) -> tuple:
        o0, failures = {}, []

        for ind, q0 in enumerate(ls):
            try:
                assert isinstance(q0, Question), f"Question {ind + 1}: Expected {Question}, got {type(q0)}."
                v3, v0, v1, v2, k0, v4 = \
                    q0.question, q0.answer, q0.type, q0.widget_requirement, q0.quid, q0.comments

                # QUID: Data [SHA3_512 Hex Digest, because why not]

                o0[k0] = {
                    StandardVariables.answer_key: v0,
                    StandardVariables.type_key: v1,
                    StandardVariables.widget_key: v2,
                    StandardVariables.question_key: v3,
                    StandardVariables.comments_key: v4,
                }

            except Exception as E:
                failures.append(str(E))
                print(traceback.format_exc())

        del ls

        o1 = o0 if re_dict else json.dumps(o0, indent=4)
        return o1, failures
