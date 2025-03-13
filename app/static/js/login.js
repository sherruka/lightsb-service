document.addEventListener("DOMContentLoaded", async function () {
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

                if (response.ok && result.redirect_to && result.access_token) {
                    // Сохраняем токен в localStorage
                    sessionStorage.setItem("access_token", result.access_token);

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

async function refreshAccessToken() {

    try{
        const response = await fetch("/api/auth/refresh", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const result = await response.json();
            sessionStorage.setItem("access_token", result.access_token);
            return result.access_token;
        } else {
            // Если refresh token невалиден, пользователь должен заново войти
            alert("Session expired, please log in again.");
            sessionStorage.removeItem("access_token");
            window.location.href = "/api/auth/login";
        }
    } catch (error) {
        console.error("Error refreshing token:", error);
        alert("Something went wrong. Please log in again.");
        window.location.href = "/api/auth/login";
    }
}
