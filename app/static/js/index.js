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

    function activateMenuItem(page) {
        menuItems.forEach(i => i.classList.remove("active"));
        const targetItem = document.querySelector(`.Menu-item[data-page="${page}"]`);
        if (targetItem) {
            targetItem.classList.add("active");
        }
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

    const redirected = await checkRedirect(); 

    if (!redirected) {
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
});