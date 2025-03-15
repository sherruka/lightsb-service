document.addEventListener("DOMContentLoaded", function(){
    const form = document.querySelector(".profile-edit-form");
    if(form){
        form.addEventListener("submit", async function(e){
            e.preventDefault();
            const formData = new FormData(form);
            const formObject = {};
            formData.forEach((value, key) => { formObject[key] = value; });
            let response = await fetch("/api/profile/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formObject)
            });
            let result = await response.json();
            if(response.ok && result.redirect_to){
                window.location.href = `/?redirect=${result.redirect_to}`;
            } else {
                alert(result.detail || "Update failed");
            }
        });
    }
});
