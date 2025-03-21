import { checkAuth } from "./checkauth.js";

document.addEventListener("DOMContentLoaded", async function () {
    let isAuthenticated = await checkAuth()
    if (isAuthenticated) {
        window.location.href = `/?redirect=profile`;
        return
    }

    const form = document.querySelector(".auth-form");
    // Флаг подтверждения очистки пробелов
    let spacesConfirmed = false;

    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault(); // Останавливаем стандартную отправку формы

            const formData = new FormData(form);
            const formObject = {};
            const trimmedFields = [];

            // Цикл обработки данных формы: удаляем лишние пробелы
            formData.forEach((value, key) => {
                const trimmedValue = value.trim();
                if (value !== trimmedValue) {
                    trimmedFields.push(key);
                }
                formObject[key] = trimmedValue;
            });

            // Если обнаружены поля с удалёнными пробелами и подтверждение ещё не дано
            if (trimmedFields.length > 0 && !spacesConfirmed) {
                alert("Обнаружены лишние пробелы в следующих полях: " + trimmedFields.join(", ") + ".\nЕсли вы согласны с внесёнными изменениями, нажмите кнопку еще раз.");
                spacesConfirmed = true;
                return; // Прерываем обработку, ждем повторного сабмита
            }

            // Валидация имени пользователя с выводом допустимых символов
            const username = formObject.username;
            const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernameRegex.test(username)) {
                alert("Имя пользователя должно быть от 3 до 20 символов и содержать только допустимые символы: a-z, A-Z, 0-9, _.");
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
                    body: JSON.stringify(formObject)
                });

                let result = await response.json();

                if (response.ok && result.redirect_to) {
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
