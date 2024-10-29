function updateCartCount(count) {
    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}
window.addEventListener('popstate', function(event) {
    // Перезагружаем страницу при нажатии кнопок "Назад" или "Вперед"
    location.reload();
});

window.addEventListener('load', function () {
    // Ваш код здесь
    console.log("Страница загружена.");

    fetch('/reload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        const totalQuantity = data.count;
        console.log('totalQuantity', totalQuantity);
        updateCartCount(totalQuantity)
    })
    .catch(error => console.error('Error:', error));
});