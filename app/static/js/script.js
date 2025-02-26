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

