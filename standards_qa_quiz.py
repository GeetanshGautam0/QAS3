# Standard declaration for *.qaQuiz files

import json, hashlib, qa_diagnostics, standards_qa_question, qa_std
from typing import *


class Standard:
    configuration_key = "config_data"
    question_key = "qa_data"
    header_key = "header"
    header_question_key = "q"
    header_configuration_key = "c"
    hash_key = 'hashes'


class Functions:
    @staticmethod
    def Import(raw_json_str: str, strict_check: bool = True) -> Tuple[
        Dict[str, Union[str, float, int, bool]],
        Tuple[standards_qa_question.Question],
        Tuple[Optional[str]]
    ]:
        """
        :param raw_json_str: Raw JSON string [STRING]
        :param strict_check: See `Checking`
        :return: tuple configuration data, passed question data, and failures

        **CHECKING**

        i) **String Checking:**

            * **Set `strict_check` to True.**
            * Uses assertion to see if hashes match.

        ii) **Soft Checking:**

            * **Set `strict_check` to False**
            * NOTE: Configuration will **still** be subject to strict checking (assertions)

        """

        # JSON > Dictionary
        # Error should NOT be caught
        j0 = json.loads(raw_json_str)
        del raw_json_str

        # Assertions
        for path in (
            Standard.question_key,
            Standard.configuration_key,
            f'{Standard.header_key}/{Standard.header_configuration_key}/{Standard.hash_key}',
            f'{Standard.header_key}/{Standard.header_question_key}/{Standard.hash_key}'
        ):
            assert qa_std.data_at_dict_path(path, j0)[0], f"Data at '{path}' not found"

        # Extract header data
        ch0_hashes = {**j0[Standard.header_key][Standard.header_configuration_key][Standard.hash_key]}
        qh0_hashes = {**j0[Standard.header_key][Standard.header_question_key][Standard.hash_key]}

        rec_hashes = {**ch0_hashes, **qh0_hashes}
        del ch0_hashes, qh0_hashes

        # Calculate hashes
        n_hashes = _create_header(j0)
        n_hashes = {
            **n_hashes[Standard.header_configuration_key][Standard.hash_key],
            **n_hashes[Standard.header_question_key][Standard.hash_key],
        }

        failures = []

        if strict_check:
            assert rec_hashes == n_hashes, "Hashes don't match; failed to load file"

        else:
            for key, hash_hex in n_hashes.items():
                if Standard.configuration_key in key:
                    assert n_hashes[key] == rec_hashes[key], \
                        f"Invalid configuration hash for `{key}`"

                else:
                    if n_hashes[key] != rec_hashes[key]:
                        failures.append(key)

        # Compile Output
        o0_c: Dict[
            str, Union[str, float, int, bool]
        ] = {**j0[Standard.configuration_key]}
        o0_q = []

        for index, (question, data) in enumerate(j0[Standard.question_key].items()):
            key = f'{Standard.question_key}{index}'
            if key in failures:
                continue

            q, (a, t, w, quid, c) = question, data

            o0_q.append(
                standards_qa_question.Question(
                    q, a, t, w, quid, c
                )
            )

        o1_q: Tuple[standards_qa_question.Question] = (*o0_q, )

        del o0_q, n_hashes, rec_hashes, j0
        return o0_c, o1_q, (*failures, )

    @staticmethod
    def Export(
            configuration_data: Dict[str, Union[str, int, float, bool]],
            questions: List[standards_qa_question.Question],
            return_as_json: bool = True
    ) -> Union[Dict, str]:
        """
        :param configuration_data: Configuration Database
        :param questions: Questions
        :param return_as_json: Return data as json? True = JSON String, False = dict
        :return: JSON String / Dictionary
        """
        # Check Configuration (qa_diagnostics)

        o0: Dict[
            str, dict
        ] = {
            Standard.header_key: {},
            Standard.configuration_key: {},
            Standard.question_key: {},
        }

        cf0, cf1 = qa_diagnostics.Configuration.general(configuration_data)

        assert cf0, \
            f"Invalid configuration data provided: {cf1}"

        o0[Standard.configuration_key] = configuration_data

        del configuration_data, cf0, cf1

        # Create Question strings (standard_qa_question)

        questions_dict, f = standards_qa_question.Functions.questions_to_json(
            questions,
            re_dict=True
        )

        assert not len(f), "The following failures occurred: \n\t* %s" % "\n\t* ".join(i for i in {f})

        o0[Standard.question_key] = {**questions_dict}

        del questions, questions_dict

        # Create Header Data
        o0[Standard.header_key] = _create_header(o0)

        return json.dumps(o0, indent=4) if return_as_json else o0


def _create_header(o):
    o0 = {**o}
    o1 = {}

    hashes = {}
    for s0, d0 in (
            (Standard.configuration_key, Standard.header_configuration_key),
            (Standard.question_key, Standard.header_question_key),
    ):
        if d0 not in hashes:
            hashes[d0] = {}

        if d0 not in o1:
            o1[d0] = {}

        for ind, (k, v) in enumerate(o0[s0].items()):
            hashes[d0][f'{s0}::{ind}'] = hashlib.sha3_512(f'{k}{v}'.encode()).hexdigest()

        o1[d0][Standard.hash_key] = hashes[d0]

    del hashes, o
    return o1
