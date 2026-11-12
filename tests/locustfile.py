
from pathlib import Path

from locust import HttpUser, task, between, constant


class AIInferenceUser(HttpUser):

    wait_time = constant(0)

    def on_start(self):
        image_path = Path(__file__).parent / "load_test.jpg"

        with open(image_path, "rb") as image:
            self.image_bytes = image.read()

    @task
    def predict_image(self):

        files = {
            "file": (
                "load_test.jpg",
                self.image_bytes,
                "image/jpeg",
            )
        }

        with self.client.post(
            "/predict",
            files=files,
            name="/predict",
            catch_response=True,
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"HTTP error: {response.status_code}"
                )
                return

            try:
                result = response.json()

                if "prediction" not in result:
                    response.failure("Missing prediction")

                elif "confidence" not in result:
                    response.failure("Missing confidence")

                else:
                    response.success()

            except Exception:
                response.failure("Invalid JSON response")
