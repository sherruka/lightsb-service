export async function refreshAccessToken() {
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
            sessionStorage.setItem("access_token", result.access_token);
            return result.access_token;
        } else {
            // Если refresh token невалиден, пользователь должен заново войти
            alert("Session expired, please log in again.");
            sessionStorage.removeItem("access_token");
            window.location.href = "/pages/login";
        }
    } catch (error) {
        console.error("Error refreshing token:", error);
        alert("Something went wrong. Please log in again.");
        window.location.href = "/pages/login";
    }
}
