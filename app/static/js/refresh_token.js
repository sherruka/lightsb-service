import { logout } from "./logout.js";

export async function refreshAccessToken(redirectOnFailure = true) {
    try{
        const response = await fetch("/api/auth/refresh", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const result = await response.json();
            sessionStorage.setItem("access_token_lightsb", result.access_token_lightsb);
            return result.access_token_lightsb;
        } else {
            console.warn("Refresh token invalid or expired.");

            logout()

            if (redirectOnFailure) {
                alert("Session expired, please log in again.");
                window.location.href = "/pages/login";
            }

            return null;
        }
    } catch (error) {
        console.error("Error refreshing token:", error);
        logout()

        if (redirectOnFailure) {
            alert("Something went wrong. Please log in again.");
            window.location.href = "/pages/login";
        }

        return null;
    }
}
