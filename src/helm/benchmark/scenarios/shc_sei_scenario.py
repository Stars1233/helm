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


class SHCSEIMedScenario(Scenario):
    """
    This dataset contains clinical notes from primary care visit encounters
    (in-person/telehealth and telephone) of children ages 6-11 years old with ADHD
    seen at Stanford's community-based primary care network, Packard Children's Health Alliance,
    between 2015-2022. All children in this dataset were prescribed at least once an ADHD
    medication (stimulants or non-stimulants) by a primary care clinician. In this
    classification task, the LLM is tasked with classifying whether the note contains
    documentation of side effect monitoring (recording of absence or presence of
    medication side effects), as recommended in clinical practice guidelines.
    From publication: https://doi.org/10.1542/peds.2024-067223
    """

    name = "shc_sei_med"
    description = (
        "ADHD-MedEffects is a benchmark designed to evaluate whether clinical notes for"
        "pediatric ADHD visits document medication side effect monitoring, which is a key recommendation"
        "in clinical practice guidelines. The dataset supports binary classification"
        "to detect presence or absence of side effect inquiries (SEI) within notes."
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
                    "You are reviewing a clinical note from health records of children "
                    "with attention deficit hyperactivity disorder (ADHD). Given the following "
                    "definitions: side Effects Inquiry (SEI): Explicit documentation by the clinician "
                    "asking about current side effects related to ADHD medications that the child is "
                    "taking or documentation of specific ADHD medication side effects experienced "
                    "by the patient. SEI does *not* include future side effects monitoring, "
                    "such as documentation of potential ADHD medication side effects, including "
                    "planning to follow patients to monitor side effects, explaining about "
                    "potential side effects of an ADHD medication. These documentations are not "
                    "categorized as SEI because they consist of a plan or an explanation about "
                    "side effects without actual side effect monitoring taking place, and "
                    "No Side Effects Inquiry (NSEI): No evidence of side effects monitoring. "
                    f"Provide an answer to the following question: {question} with the following context: {context} "
                    ", Answer the question with a 'A' for yes or 'B' for no. Do not provide any additional "
                    "details or response, just a simple A or B response."
                )
                data[prompt] = answer
        return data

    def get_instances(self, output_path: str) -> List[Instance]:
        check_file_exists(self.data_path, msg=f"[SHCSEIMedScenario] Required data file not found: '{self.data_path}'")
        instances: List[Instance] = []
        benchmark_data = self.create_benchmark(self.data_path)

        for prompt, answer in benchmark_data.items():
            assert answer in SHCSEIMedScenario.POSSIBLE_ANSWER_CHOICES
            references: List[Reference] = [
                Reference(Output(text=pred_answer), tags=[CORRECT_TAG] if pred_answer == answer else [])
                for pred_answer in SHCSEIMedScenario.POSSIBLE_ANSWER_CHOICES
            ]
            instances.append(
                Instance(
                    input=Input(text=prompt),
                    references=references,  # [Reference(Output(text=answer), tags=[CORRECT_TAG])],
                    split=TEST_SPLIT,
                )
            )

        return instances
