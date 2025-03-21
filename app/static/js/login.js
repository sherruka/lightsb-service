import { checkAuth } from "./checkauth.js";

document.addEventListener("DOMContentLoaded", async function () {
    let isAuthenticated = await checkAuth()
    if (isAuthenticated) {
        window.location.href = `/?redirect=profile`;
    }

    const form = document.querySelector(".auth-form");

    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault(); // Останавливаем стандартную отправку формы

            const formData = new FormData(form); // Сбор данных формы

            // Преобразуем данные формы в объект
            const formObject = {};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });

            formObject.remember_me = formData.has("remember_me");

            try {
                // Отправка данных на сервер
                let response = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(formObject), // Отправляем данные как JSON
                    credentials: "include",
                });

                let result = await response.json();

                if (response.ok && result.redirect_to && result.access_token_lightsb) {
                    // Сохраняем токен в sessionStorage
                    sessionStorage.setItem("access_token_lightsb", result.access_token_lightsb);

                    // Перенаправление на нужную страницу после регистрации
                    window.location.href = `/?redirect=${result.redirect_to}`;
                } else {
                    alert(result.detail || "Login failed");
                }
            }catch (error) {
                    console.error("Error during login:", error);
                    alert("Something went wrong. Please try again later.");
            }
        });
    }
});
