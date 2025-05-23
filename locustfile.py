import logging
import os
import random
import time
from pathlib import Path

from locust import HttpUser, TaskSet, between, task
from locust.exception import StopUser

logger = logging.getLogger(__name__)

IMG_DIR = Path(os.getenv("LSB_IMG_DIR", "tests/load_images"))
WAIT_MIN, WAIT_MAX = 1, 5


class UserBehavior(TaskSet):
    def on_start(self):
        """
        Login at the beginning of a user session.
        """
        self.client.timeout = 60
        self.client.verify = False
        self.token = None
        self.username = f"testuser_{random.randint(1000, 9999)}"
        self.email = f"{self.username}@test.com"
        self.password = "Password123!"

        self.register()
        self.login()

        if not self.token:
            raise StopUser("Failed to authenticate")

    def register(self):
        """
        Register a new user.
        """
        try:
            response = self.client.post(
                "/api/auth/register",
                json={
                    "username": self.username,
                    "email": self.email,
                    "password": self.password,
                    "password_confirm": self.password,
                },
            )

            if response.status_code not in [201, 409]:
                logger.error(
                    f"Registration failed with status {response.status_code}: {response.text}"
                )
        except Exception as e:
            logger.error(f"Registration exception: {str(e)}")

    def login(self):
        """
        Login and store the authentication token.
        """
        try:
            response = self.client.post(
                "/api/auth/login",
                json={
                    "identifier": self.username,
                    "password": self.password,
                    "remember_me": False,
                },
            )

            if response.status_code == 200:
                self.token = response.json().get("access_token_lightsb")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                logger.error(
                    f"Login failed with status {response.status_code}: {response.text}"
                )
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")

    def refresh_token(self):
        """
        Refresh the authentication token if needed.
        """
        try:
            response = self.client.post("/api/auth/refresh")
            if response.status_code == 200:
                self.token = response.json().get("access_token_lightsb")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            return False
        except Exception:
            return False

    @task(1)
    def view_home(self):
        """
        View the home page.
        """
        self.client.get("/pages/home")

    @task(1)
    def view_about(self):
        """
        View the about page.
        """
        self.client.get("/pages/aboutUs")

    @task(2)
    def view_profile(self):
        """
        View the user profile.
        """
        with self.client.get("/api/profile", catch_response=True) as response:
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_token():
                    response.success()
                else:
                    self.login()
            elif response.status_code != 200:
                response.failure(f"Failed to get profile: {response.status_code}")

    @task(3)
    def update_profile(self):
        """
        Update the user profile.
        """
        with self.client.post(
            "/api/profile/update",
            json={
                "full_name": f"Test User {random.randint(1000, 9999)}",
                "position": "QA Engineer",
                "date_of_birth": "1990-01-01",
            },
            catch_response=True,
        ) as response:
            if response.status_code == 401:
                if self.refresh_token():
                    response.success()
                else:
                    self.login()
            elif response.status_code != 200:
                response.failure(f"Failed to update profile: {response.status_code}")

    @task(5)
    def generate_image(self):
        """
        Upload an image and generate aged versions.
        This is the main functionality to test.
        """
        test_images_dir = IMG_DIR
        image_files = list(test_images_dir.glob("*.jpg")) + list(
            test_images_dir.glob("*.png")
        )

        if not image_files:
            logger.error("No test images found!")
            return

        image_path = random.choice(image_files)

        start_time = time.time()

        with open(image_path, "rb") as image_file:
            with self.client.post(
                "/api/generate",
                files={"file": (image_path.name, image_file, "image/jpeg")},
                catch_response=True,
            ) as response:
                if response.status_code == 401:
                    if self.refresh_token():
                        response.success()
                    else:
                        self.login()
                        return
                elif response.status_code != 200:
                    response.failure(
                        f"Failed to generate image: {response.status_code}"
                    )
                    return

                processing_time = time.time() - start_time


class WebsiteUser(HttpUser):
    host = "https://nginx"
    tasks = [UserBehavior]
    wait_time = between(WAIT_MIN, WAIT_MAX)
