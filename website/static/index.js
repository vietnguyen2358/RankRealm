document.addEventListener('DOMContentLoaded', () => {
    let alertMessages = document.querySelectorAll('.alert');

    alertMessages.forEach((alert) => {
        setTimeout(() => {
            alert.remove();
        }, 3000);
    })

    let username = document.querySelector('.dropdown > .nav-link.dropdown-toggle');
    let dropdown = document.querySelector('.dropdown-menu');

    function showDropdown() {
        dropdown.classList.add('show');
    }

    function hideDropdown() {
        dropdown.classList.remove('show');
    }

    username.addEventListener('mouseenter', showDropdown);

    username.addEventListener('mouseleave', hideDropdown);

    dropdown.addEventListener('mouseenter', showDropdown);

    dropdown.addEventListener('mouseleave', hideDropdown);
})