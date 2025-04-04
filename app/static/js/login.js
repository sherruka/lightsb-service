import { checkAuth } from "./checkauth.js";

document.addEventListener("DOMContentLoaded", async function () {
    // Hide the login form initially until auth status is known.
    const form = document.querySelector(".auth-form");
    if (form) form.style.display = "none";

    let isAuthenticated = await checkAuth();
    if (isAuthenticated) {
        window.location.href = "/?redirect=profile";
        return;
    }

    // Show the form after the check completes.
    if (form) {
        // Remove the inline display style to allow the default CSS to apply.
        form.style.display = "";
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form); // Gather form data

        // Convert form data to an object
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });

        formObject.remember_me = formData.has("remember_me");

        try {
            // Send login data to the server
            let response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formObject), // Send data as JSON
                credentials: "include",
            });

            let result = await response.json();

            if (response.ok && result.redirect_to && result.access_token_lightsb) {
                // Save the access token in sessionStorage
                sessionStorage.setItem("access_token_lightsb", result.access_token_lightsb);

                // Redirect after successful login
                window.location.href = `/?redirect=${result.redirect_to}`;
            } else {
                alert(result.detail || "Login failed");
            }
        } catch (error) {
            console.error("Error during login:", error);
            alert("Something went wrong. Please try again later.");
        }
    });
});
