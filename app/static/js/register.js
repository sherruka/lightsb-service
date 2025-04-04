import { checkAuth } from "./checkauth.js";

document.addEventListener("DOMContentLoaded", async function () {
    // Hide the registration form initially until auth status is known.
    const form = document.querySelector(".auth-form");
    if (form) form.style.display = "none";

    let isAuthenticated = await checkAuth();
    if (isAuthenticated) {
        window.location.href = "/?redirect=profile";
        return;
    }

    // Show the form after the auth check completes.
    if (form) {
        // Remove the inline display style to allow the default CSS to apply.
        form.style.display = "";
    }

    // Flag for confirming removal of extra spaces
    let spacesConfirmed = false;

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);
        const formObject = {};
        const trimmedFields = [];

        // Process form data: trim spaces from input values
        formData.forEach((value, key) => {
            const trimmedValue = value.trim();
            if (value !== trimmedValue) {
                trimmedFields.push(key);
            }
            formObject[key] = trimmedValue;
        });

        // If extra spaces were removed and confirmation has not been given, alert and wait for re-submit
        if (trimmedFields.length > 0 && !spacesConfirmed) {
            alert("Extra spaces were detected in the following fields: " + trimmedFields.join(", ") + ".\nIf you agree with the changes made, click the button again.");
            spacesConfirmed = true;
            return; // Halt processing until the user confirms
        }

        // Validate username (allowing a-z, A-Z, 0-9, _ and between 3 to 20 characters)
        const username = formObject.username;
        const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
        if (!usernameRegex.test(username)) {
            alert("The username must be between 3 and 20 characters and contain only valid characters: a-z, A-Z, 0-9, _.");
            return;
        }

        // Validate email address
        const email = formObject.email;
        const emailRegex = /^\S+@\S+\.\S+$/;
        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        // Validate password length
        const password = formObject.password;
        if (password.length < 8) {
            alert("The password must contain a minimum of 8 characters.");
            return;
        }

        // Validate password confirmation
        const passwordConfirm = formObject.password_confirm;
        if (password !== passwordConfirm) {
            alert("The passwords don't match!");
            return;
        }

        // Send registration data to the server
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
                alert(result.detail || "Registration failed");
            }
        } catch (error) {
            console.error("Error when sending data:", error);
            alert("There was an error during registration. Please try again later.");
        }
    });
});
