from dataclasses import dataclass

@dataclass
class Employee(frozen=True):

    job_title: str
    given_name: str
    family_name: str

    personal_email: str
    work_email: str

    phone_number: str

    operating_stores: list[str]

    