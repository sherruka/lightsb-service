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

            // Отправка данных на сервер
            let response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formObject) // Отправляем данные как JSON
            });

            let result = await response.json();

            if (response.ok && result.redirect_to) {
                // Перенаправление на нужную страницу после регистрации
                window.location.href = `/?redirect=${result.redirect_to}`;
            } else {
                alert(result.detail || "Login failed");
            }
        });
    }
});
