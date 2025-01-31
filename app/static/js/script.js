document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll('.Menu-item');

    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active'); 
        });
    });
});
