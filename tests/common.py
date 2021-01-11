"""Common code for aioekosystemwroclaw tests."""
import os

TEST_LOCALIZATION_ID = 539489
TEST_STREET_ID = 103


def load_fixture(file_name) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", file_name)
    with open(path, "r", encoding="utf-8") as file_obj:
        return file_obj.read()
