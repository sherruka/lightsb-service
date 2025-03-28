document.addEventListener("DOMContentLoaded", async function () {
    const menuItems = document.querySelectorAll(".Menu-item");
    const contentArea = document.querySelector(".Content-area");

    async function loadPage(page) {
        try {
            const response = await fetch(`/pages/${page}`);
            if (response.ok) {
                contentArea.innerHTML = await response.text();
            } else {
                contentArea.innerHTML = "<h2>Page not found</h2>";
            }
        } catch (error) {
            contentArea.innerHTML = "<h2>Error loading page</h2>";
        }
    }

    function activateMenuItem(page) {
        menuItems.forEach(i => i.classList.remove("active"));
        const targetItem = document.querySelector(`.Menu-item[data-page="${page}"]`);
        if (targetItem) targetItem.classList.add("active");
    }

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

    if (!await checkRedirect()) {
        await loadPage("home");
        activateMenuItem("home");
    }

    menuItems.forEach(item => {
        item.addEventListener("click", async function () {
            const page = this.dataset.page;
            activateMenuItem(page);
            await loadPage(page);
        });
    });

    contentArea.addEventListener("click", async function (e) {
        if (e.target.matches(".edit-profile-btn")) {
            e.preventDefault();
            await loadPage("profile-change");
        }
    });
});
