document.addEventListener('DOMContentLoaded', () => {
    let alertMessages = document.querySelectorAll('.alert');

    alertMessages.forEach((alert) => {
        setTimeout(() => {
            alert.remove();
        }, 3000);
    })
})