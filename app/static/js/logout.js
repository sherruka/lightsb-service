export async function logout() {
    sessionStorage.removeItem("access_token_lightsb");
    await fetch("/api/logout", { method: "POST", credentials: "include" });
}
