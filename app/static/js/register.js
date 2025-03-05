document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".auth-form");

    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault(); // Останавливаем стандартную отправку формы

            const formData = new FormData(form); // Сбор данных формы

            // Преобразуем данные формы в объект
            const formObject = {};
            formData.forEach((value, key) => {
                formObject[key] = value.trim(); // Удаляем пробелы в начале и конце
            });

            // Валидация имени пользователя
            const username = formObject.username;
            const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernameRegex.test(username)) {
                alert("Имя пользователя должно быть от 3 до 20 символов и содержать только буквы, цифры и символы подчеркивания.");
                return;
            }

            // Валидация адреса электронной почты
            const email = formObject.email;
            const emailRegex = /^\S+@\S+\.\S+$/;
            if (!emailRegex.test(email)) {
                alert("Пожалуйста, введите корректный адрес электронной почты.");
                return;
            }

            // Валидация пароля
            const password = formObject.password;
            if (password.length < 8) {
                alert("Пароль должен содержать минимум 8 символов.");
                return;
            }

            // Проверка на совпадение паролей
            const passwordConfirm = formObject.password_confirm;
            if (password !== passwordConfirm) {
                alert("Пароли не совпадают!");
                return;
            }

            // Отправка данных на сервер
            try {
                let response = await fetch("/api/auth/register", {
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
                    alert(result.detail || "Регистрация не удалась");
                }
            } catch (error) {
                console.error("Ошибка при отправке данных:", error);
                alert("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.");
            }
        });
    }
});
