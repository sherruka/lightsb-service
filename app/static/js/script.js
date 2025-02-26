document.addEventListener("DOMContentLoaded", async function () {
    const menuItems = document.querySelectorAll(".Menu-item");
    const contentArea = document.querySelector(".Content-area");

    async function loadPage(page) {
        try {
            const response = await fetch(`/pages/${page}`);
            if (response.ok) {
                const html = await response.text();
                contentArea.innerHTML = html;
            } else {
                contentArea.innerHTML = "<h2>Page not found</h2>";
            }
        } catch (error) {
            contentArea.innerHTML = "<h2>Error loading page</h2>";
        }
    }

    await loadPage("home");

    menuItems.forEach(item => {
        if (item.dataset.page === "home") {
            item.classList.add("active");
        }
    });

    menuItems.forEach(item => {
        item.addEventListener("click", async function () {
            menuItems.forEach(i => i.classList.remove("active"));
            this.classList.add("active");

            const page = this.dataset.page;
            await loadPage(page);
        });
    });
});

// Получаем элементы
const loginLink = document.getElementById('login-link');
const registerLink = document.getElementById('register-link');
const loginModal = document.getElementById('login-modal');
const registerModal = document.getElementById('register-modal');
const closeLogin = document.getElementById('close-login');
const closeRegister = document.getElementById('close-register');

// Функция для открытия модального окна
function openModal(modal) {
    modal.style.display = 'block';
}

// Функция для закрытия модального окна
function closeModal(modal) {
    modal.style.display = 'none';
}

// Открытие модальных окон при клике на ссылки
loginLink.addEventListener('click', (e) => {
    e.preventDefault();
    openModal(loginModal);
});

registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    openModal(registerModal);
});

// Закрытие модальных окон при клике на крестик
closeLogin.addEventListener('click', () => closeModal(loginModal));
closeRegister.addEventListener('click', () => closeModal(registerModal));

// Закрытие модальных окон при клике вне их области
window.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        closeModal(loginModal);
    }
    if (e.target === registerModal) {
        closeModal(registerModal);
    }
});
