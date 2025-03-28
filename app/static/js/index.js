import { refreshAccessToken } from "./refresh_token.js";
import { checkAuth } from "./checkauth.js";
import { logout } from "./logout.js";

document.addEventListener("DOMContentLoaded", async function () {
    // Initially hide auth-related UI elements to prevent any flash until check completes.
    document.querySelectorAll(".unauthorized, .authorized").forEach(el => el.style.display = "none");

    let isAuthenticated = await updateAuthUI();

    const menuItems = document.querySelectorAll(".Menu-item");
    const contentArea = document.querySelector(".Content-area");

    async function updateAuthUI() {
        // Ensure elements are hidden while the auth check is pending.
        document.querySelectorAll(".unauthorized, .authorized").forEach(el => el.style.display = "none");

        let isAuthenticated = await checkAuth();
        document.querySelectorAll(".unauthorized").forEach(el => el.style.display = isAuthenticated ? "none" : "block");
        document.querySelectorAll(".authorized").forEach(el => el.style.display = isAuthenticated ? "block" : "none");

        return isAuthenticated;
    }

    if (isAuthenticated) {
        try {
            let accessToken = sessionStorage.getItem("access_token_lightsb");
            let response = await fetch("/api/user", {
                method: "GET",
                credentials: "include",
                headers: {
                    "Authorization": `Bearer ${accessToken}`
                }
            });

            if (!response.ok) throw new Error("Failed to load user");

            let data = await response.json(); 

            // Insert the username into the profile text elements
            document.querySelectorAll(".Profile-txt").forEach(el => el.textContent = data.username);

        } catch (error) {
            console.error("Error loading profile:", error);
        }
    }

    // Function to load pages
    async function loadPage(page) {
        try {
            const response = await fetch(`/pages/${page}`);
            if (response.ok) {
                contentArea.innerHTML = await response.text();
                // Initialize page-specific handlers after the content loads
                requestAnimationFrame(() => initPage(page));
            } else {
                contentArea.innerHTML = "<h2>Page not found</h2>";
            }
        } catch (error) {
            contentArea.innerHTML = "<h2>Error loading page</h2>";
        }
    }

    // Function to activate a menu item
    function activateMenuItem(page) {
        menuItems.forEach(i => i.classList.remove("active"));
        const targetItem = document.querySelector(`.Menu-item[data-page="${page}"]`);
        if (targetItem) targetItem.classList.add("active");
    }

    // Function to check for redirect parameters
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

    // Load home page or redirect page
    if (!await checkRedirect()) {
        await loadPage("home");
        activateMenuItem("home");
    }

    // Menu item click handler
    menuItems.forEach(item => {
        item.addEventListener("click", async function () {
            const page = this.dataset.page;
            activateMenuItem(page);
            await loadPage(page);
        });
    });

    // Initialize page-specific functionality
    function initPage(page) {
        if (page === "profile") {
            initProfilePage();  // Profile page initialization
        } else if (page === "profile-change") {
            initProfileEditPage();  // Profile edit page initialization
        } else if (page === "generator") {
            initGeneratorPage();  // Generator page initialization
        }         
    }

    async function initProfilePage() {
        let isAuthenticated = await updateAuthUI();

        const logoutBtn = document.querySelector('.logout-btn');
        const modal = document.getElementById("logout-modal");
        if (modal) modal.style.display = "none";

        const confirmLogout = document.getElementById("confirm-logout");
        const cancelLogout = document.getElementById("cancel-logout");

        const editButton = document.querySelector('.edit-profile-btn');

        if (isAuthenticated) {
            try {
                let accessToken = sessionStorage.getItem("access_token_lightsb");
                let response = await fetch("/api/profile", {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`
                    }
                });

                if (!response.ok) throw new Error("Failed to load profile");
        
                let data = await response.json();
        
                // Insert profile data into the appropriate page elements
                document.querySelectorAll(".Info-item .Info-value")[0].textContent = data.full_name;
                document.querySelectorAll(".Info-item .Info-value")[1].textContent = data.position;
                document.querySelectorAll(".Info-item .Info-value")[2].textContent = data.date_of_birth;

            } catch (error) {
                console.error("Error loading profile:", error);
            }
        }

        if (editButton) {
            editButton.addEventListener('click', async function (e) {
                e.preventDefault();
                await loadPage("profile-change");
            });
        }
    
        // Open logout modal
        logoutBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "flex";
        });
    
        // Close modal on cancel
        cancelLogout.addEventListener("click", function () {
            modal.style.display = "none";
        });
    
        // Confirm logout action
        confirmLogout.addEventListener("click", async function () {
            modal.style.display = "none";
    
            try {
                logout();
                window.location.reload();
            } catch (error) {
                console.error("Ошибка выхода:", error);
            }
        });
    
        // Close modal when clicking outside of it
        window.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }

    // Profile edit page initialization
    async function initProfileEditPage() {
        let isAuthenticated = await updateAuthUI();

        if (!isAuthenticated) {
            alert("You are not logged in, please log in.");
            window.location.href = "/pages/login";
        }

        const form = document.querySelector(".profile-edit-form");
        if (!form) return;

        if (isAuthenticated) {
            try {
                let accessToken = sessionStorage.getItem("access_token_lightsb");
                let response = await fetch("/api/profile", {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`
                    }
                });

                if (!response.ok) throw new Error("Failed to load profile");
        
                let data = await response.json();
        
                // Populate form fields with profile data
                document.getElementById("full_name").value = data.full_name;
                document.getElementById("position").value = data.position;
                document.getElementById("date_of_birth").value = data.date_of_birth;

            } catch (error) {
                console.error("Error loading profile:", error);
            }
        }

        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            const formObject = {};
            formData.forEach((value, key) => { formObject[key] = value.trim(); });

            const fullName = formObject.full_name;
            const fullNameRegex = /^[А-ЯЁA-Z][а-яёa-z]+\s[А-ЯЁA-Z][а-яёa-z]+(?:\s[А-ЯЁA-Z][а-яёa-z]+)?$/;
            if (!fullNameRegex.test(fullName)) {
                alert("Enter correct full name (First and Last name is required, first letter in uppercase)");
                return;
            }
    
            async function sendProfileUpdate(token) {
                return fetch("/api/profile/update", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify(formObject),
                });
            }

            let accessToken = sessionStorage.getItem("access_token_lightsb");
            let response = await sendProfileUpdate(accessToken);

            if (response.status === 401) {  // Token expired
                const newAccessToken = await refreshAccessToken();

                if (newAccessToken) {
                    // Retry request with new token
                    response = await sendProfileUpdate(newAccessToken);
                } else {
                    alert("Session expired, please log in again.");
                    window.location.href = "/pages/login";
                }
            }

            try {
                let result = await response.json();
                if (response.ok && result.redirect_to) {
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

    async function initGeneratorPage() {
        let isAuthenticated = await updateAuthUI();
    }
});
