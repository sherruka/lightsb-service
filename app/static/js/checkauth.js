import { refreshAccessToken } from "./refresh_token.js";

export async function checkAuth() {
    let accessToken = sessionStorage.getItem("access_token_lightsb");

    if (accessToken) {
        try {
            const response = await fetch("/api/protected-route", {
                headers: { "Authorization": `Bearer ${accessToken}` }
            });

            if (!response.ok) {
                throw new Error("The token is invalid");
            }

            return true
        } catch (error) {
            const newAccessToken = await refreshAccessToken(false);

            if (newAccessToken) {
                return true
            }
            return false
        }
    } else {
        const newAccessToken = await refreshAccessToken(false);

        if (newAccessToken) {
            return true
        }
        return false
    }
}