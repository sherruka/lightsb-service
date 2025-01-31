document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll('.Menu-item');
    const contentArea = document.querySelector('.Content-area');

    const pages = {
        home: `
            <span class="Main-text">Main information</span>
            <span class="Second-text">Welcome to the LightSB service!</span>
        `,
        generator: `
            <span class="Main-text">Generator</span>
            <span class="Second-text">Create something unique with our generator.</span>
        `,
        aboutUs: `
            <span class="Main-text">About Us</span>
            <span class="Second-text">Learn more about our team and mission.</span>
        `,
        profile: `
            <span class="Main-text">Profile</span>
            <span class="Second-text">Manage your account and settings.</span>
        `
    };

    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            if (this.classList.contains("Home")) {
                contentArea.innerHTML = pages.home;
            } else if (this.classList.contains("Generator")) {
                contentArea.innerHTML = pages.generator;
            } else if (this.classList.contains("About-us")) {
                contentArea.innerHTML = pages.aboutUs;
            } else if (this.classList.contains("Profile")) {
                contentArea.innerHTML = pages.profile;
            }
        });
    });
});
