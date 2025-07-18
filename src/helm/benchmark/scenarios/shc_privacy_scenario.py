import sys
import csv
from typing import Dict, List

from helm.benchmark.scenarios.scenario import (
    Input,
    Scenario,
    Instance,
    TEST_SPLIT,
    CORRECT_TAG,
    Reference,
    Output,
)
from helm.common.general import check_file_exists

csv.field_size_limit(sys.maxsize)


class SHCPRIVACYMedScenario(Scenario):
    """
    This dataset features messages sent generated by an LLM from patient clinical notes data.
    The scenario evaluates the ability of an LLM to determine if any potentially confidential
    information about the patient was included. From publication: https://doi.org/10.1001/jamapediatrics.2024.4438
    """

    name = "shc_privacy_med"
    description = (
        "PrivacyDetection is a benchmark composed of patient portal messages submitted by"
        "patients or caregivers. The task is to determine whether the message contains any"
        "confidential or privacy-leaking information that should be protected."
    )
    tags = ["knowledge", "reasoning", "biomedical"]

    POSSIBLE_ANSWER_CHOICES: List[str] = ["A", "B"]

    def __init__(self, data_path: str):
        super().__init__()
        self.data_path = data_path

    def create_benchmark(self, csv_path) -> Dict[str, str]:
        data = {}
        with open(csv_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = row["prompt"]
                context = row["context"]
                answer = row["label"]
                prompt = (
                    "You are reviewing clinical messages in order to determine if any confidential "
                    f"information was included. Please answer the following question: {question} with the "
                    f"following context: {context} , Answer the question with a 'A' for yes or 'B' "
                    "for no. Do not provide any additional details or response, just a simple A or B response."
                )
                data[prompt] = answer
        return data

    def get_instances(self, output_path: str) -> List[Instance]:
        check_file_exists(
            self.data_path, msg=f"[SHCPRIVACYMedScenario] Required data file not found: '{self.data_path}'"
        )
        instances: List[Instance] = []
        benchmark_data = self.create_benchmark(self.data_path)

        for prompt, answer in benchmark_data.items():
            assert answer in SHCPRIVACYMedScenario.POSSIBLE_ANSWER_CHOICES
            references: List[Reference] = [
                Reference(Output(text=pred_answer), tags=[CORRECT_TAG] if pred_answer == answer else [])
                for pred_answer in SHCPRIVACYMedScenario.POSSIBLE_ANSWER_CHOICES
            ]
            instances.append(
                Instance(
                    input=Input(text=prompt),
                    references=references,  # [Reference(Output(text=answer), tags=[CORRECT_TAG])],
                    split=TEST_SPLIT,
                )
            )

        return instances
