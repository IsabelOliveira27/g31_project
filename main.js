document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll("a");
    
    links.forEach(link => {
        const button = link.querySelector("button");
        if (button && button.hasAttribute("disabled")) {
            link.addEventListener("click", function (e) {
                e.preventDefault();
            });
        }
    });
});