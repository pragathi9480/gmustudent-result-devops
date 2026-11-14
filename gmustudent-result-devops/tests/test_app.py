import os
import sys

import pytest

# Make sure Python imports the project's own app.py (one folder above /tests),
# not some other app.py that happens to be elsewhere on the machine.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app import app, calculate_result  # noqa: E402


def test_calculate_pass_result():
    result = calculate_result("Ravi", [80, 75, 90])

    assert result["name"] == "Ravi"
    assert result["total"] == 245
    assert result["percentage"] == pytest.approx(81.6667, rel=1e-4)
    assert result["status"] == "PASS"


def test_calculate_fail_result():
    result = calculate_result("Sita", [90, 30, 85])

    assert result["total"] == 205
    assert result["status"] == "FAIL"


def test_name_is_trimmed():
    result = calculate_result("  Aman  ", [50, 60, 70])

    assert result["name"] == "Aman"


@pytest.mark.parametrize(
    "marks",
    [
        [-1, 50, 50],
        [101, 50, 50],
        [50, 50],
        [50, 50, 50.5],
        [True, 50, 50],
    ],
)
def test_invalid_marks_are_rejected(marks):
    with pytest.raises(ValueError):
        calculate_result("Ravi", marks)


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        calculate_result("   ", [50, 60, 70])


def test_home_page_opens():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Student Result Management" in response.data


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


if __name__ == "__main__":
    # Lets you run:  py test_app.py   (otherwise nothing would execute)
    sys.exit(pytest.main([__file__, "-v"]))