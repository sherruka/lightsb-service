import { refreshAccessToken } from "./refresh_token.js";

document.addEventListener("DOMContentLoaded", async function () {
    const menuItems = document.querySelectorAll(".Menu-item");
    const contentArea = document.querySelector(".Content-area");

    // Функция загрузки страниц
    async function loadPage(page) {
        try {
            const response = await fetch(`/pages/${page}`);
            if (response.ok) {
                contentArea.innerHTML = await response.text();
                // После загрузки страницы инициализируем обработчики для этой страницы
                requestAnimationFrame(() => initPage(page));
            } else {
                contentArea.innerHTML = "<h2>Page not found</h2>";
            }
        } catch (error) {
            contentArea.innerHTML = "<h2>Error loading page</h2>";
        }
    }

    // Функция активации элемента меню
    function activateMenuItem(page) {
        menuItems.forEach(i => i.classList.remove("active"));
        const targetItem = document.querySelector(`.Menu-item[data-page="${page}"]`);
        if (targetItem) targetItem.classList.add("active");
    }

    // Функция проверки редиректа
    async function checkRedirect() {
        const params = new URLSearchParams(window.location.search);
        if (params.get("redirect") === "profile") {
            await loadPage("profile");
            activateMenuItem("profile");
            history.replaceState({}, "", window.location.pathname);
            return true;
        }
        return false;
    }

    // Загрузка домашней страницы или страницы редиректа
    if (!await checkRedirect()) {
        await loadPage("home");
        activateMenuItem("home");
    }

    // Обработчик кликов по меню
    menuItems.forEach(item => {
        item.addEventListener("click", async function () {
            const page = this.dataset.page;
            activateMenuItem(page);
            await loadPage(page);
        });
    });

    // Функция для инициализации страниц с их специфичными обработчиками
    function initPage(page) {
        if (page === "profile") {
            initProfilePage();  // Инициализация страницы профиля
        } else if (page === "profile-change") {
            initProfileEditPage();  // Инициализация страницы редактирования профиля
        }
    }

    function initProfilePage() {
        const editButton = document.querySelector('.edit-profile-btn');
        if (editButton) {
            editButton.addEventListener('click', async function (e) {
                e.preventDefault();
                await loadPage("profile-change");
            });
        }
    }

    // Инициализация страницы редактирования профиля
    function initProfileEditPage() {
        const form = document.querySelector(".profile-edit-form");
        if (!form) return;

        
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            const formObject = {};
            formData.forEach((value, key) => { formObject[key] = value; });

            async function sendProfileUpdate(token) {
                return fetch("/api/profile/update", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(formObject),
                });
            }

            let accessToken = sessionStorage.getItem("access_token");
            let response = await sendProfileUpdate(accessToken);

            if (response.status === 401) {  // Токен истек
                const newAccessToken = await refreshAccessToken();

                if (newAccessToken) {
                    // Повторяем запрос с новым токеном
                    response = await sendProfileUpdate(newAccessToken);
                }
            }

            try {
                let result = await response.json();
                if(response.ok && result.redirect_to){
                    window.location.href = `/?redirect=${result.redirect_to}`;
                } else {
                    alert(result.detail || "Update failed");
                }
            } catch (error) {
                console.error("Error processing the response:", error);
                alert("Server error. Try again later.");
            }
        });
        
    }
});
