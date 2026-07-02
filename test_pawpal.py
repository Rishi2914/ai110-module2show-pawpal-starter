from pawpal_system import Pet, PetCareTask


def make_task(title="Walk"):
    return PetCareTask(title, 30, "high", "exercise", True, "daily")


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Each add_task call should grow the pet's task list by one."""
    pet = Pet("Buddy", "Dog", 3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task("Walk"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(make_task("Feed"))
    assert len(pet.get_tasks()) == 2
