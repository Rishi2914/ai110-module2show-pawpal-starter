class Owner:
    def __init__(self, name: str, time_available_minutes: int, preferences: list[str]):
        self.name = name
        self.time_available_minutes = time_available_minutes
        self.preferences = preferences

    def add_pet(self, pet: "Pet") -> None:
        pass

    def set_time_available(self, minutes: int) -> None:
        pass

    def get_pets(self) -> list["Pet"]:
        pass


class Pet:
    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age

    def add_task(self, task: "PetCareTask") -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def get_tasks(self) -> list["PetCareTask"]:
        pass

    def clear_tasks(self) -> None:
        pass


class PetCareTask:
    def __init__(self, title: str, duration_minutes: int, priority: str, category: str, is_recurring: bool, frequency: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_recurring = is_recurring
        self.frequency = frequency

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


class Scheduler:
    def __init__(self, start_time: str, time_limit_minutes: int):
        self.start_time = start_time
        self.time_limit_minutes = time_limit_minutes

    def build_plan(self, pet: "Pet", owner: "Owner") -> "DailyPlan":
        pass

    def sort_tasks(self, tasks: list) -> list["PetCareTask"]:
        pass

    def filter_tasks(self, tasks: list, time_remaining: int) -> list["PetCareTask"]:
        pass

    def check_conflicts(self, items: list) -> bool:
        pass


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_items: list["ScheduledItem"] = []
        self.total_duration_minutes: int = 0
        self.skipped_tasks: list[str] = []

    def add_item(self, item: "ScheduledItem") -> None:
        pass

    def skip_task(self, task: "PetCareTask", reason: str) -> None:
        pass

    def display(self) -> str:
        pass

    def explain(self) -> str:
        pass

    def get_summary(self) -> dict:
        pass


class ScheduledItem:
    def __init__(self, task: "PetCareTask", start_time: str, end_time: str, reason: str):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def duration(self) -> int:
        pass

    def to_dict(self) -> dict:
        pass
