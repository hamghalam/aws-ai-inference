
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["model"] == "MobileNetV2"
    assert data["device"] == "cpu"


def test_invalid_file_type():
    response = client.post(
        "/predict",
        files={
            "file": (
                "document.txt",
                b"not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only JPEG, PNG, and WebP" in response.json()["detail"]


def test_successful_image_prediction():
    image_path = Path(__file__).parent / "load_test.jpg"

    with image_path.open("rb") as image:
        response = client.post(
            "/predict",
            files={
                "file": (
                    "load_test.jpg",
                    image,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["prediction"], str)
    assert data["prediction"] != ""
    assert isinstance(data["confidence"], (int, float))
    assert 0 <= data["confidence"] <= 1


def test_invalid_image_content():
    response = client.post(
        "/predict",
        files={
            "file": (
                "invalid.jpg",
                b"this is not a valid image",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400
    assert "Invalid image or inference error" in response.json()["detail"]
