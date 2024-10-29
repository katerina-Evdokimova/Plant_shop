function updateCartCount(count) {
    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

// Обработчик нажатий на стрелки "назад" и "вперед"
window.addEventListener('popstate', function(event) {
    console.log('State changed to:');
    if (event.state) {
        // Здесь вы можете обновить состояние страницы на основе данных в истории
        console.log('State changed to:', event.state);
        // Обновите содержимое страницы на основе сохранённого состояния
        // Например, обновите количество товаров в корзине, фильтры, и т.д.
        location.href = location.href;

    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Добавление товара в корзину
    document.querySelectorAll('.add-to-cart').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');
            const addToCartButton = this;
            const quantityControl = addToCartButton.nextElementSibling;
            console.log('productId', productId);
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                // Обновляем количество товара
                const newQuantity = data.cart[productId];
                
                // Скрываем кнопку "Добавить в корзину" и показываем панель управления количеством
                addToCartButton.style.display = 'none';
                quantityControl.style.display = 'flex';  // Показываем плашку с кнопками + и -

                // Обновляем количество товара
                quantityControl.querySelector('.quantity').textContent = newQuantity;
                console.log('newQuantity', newQuantity);
                console.log('quantityControl', quantityControl);

                const totalQuantity = Object.values(data.cart).reduce((total, quantity) => total + quantity, 0);
                console.log('totalQuantity', totalQuantity); // Вывод: 6
                updateCartCount(totalQuantity)
            })
            .catch(error => console.error('Error:', error))
            .fetch('EROOOOOOOOR', error);
        });
    });

    // Увеличение количества товара
    document.querySelectorAll('.quantity-btn.increase').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');
            const quantityElem = this.previousElementSibling;

            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                // Обновляем количество товара
                quantityElem.textContent = data.cart[productId];

                const totalQuantity = Object.values(data.cart).reduce((total, quantity) => total + quantity, 0);
                console.log('totalQuantity', totalQuantity);
                updateCartCount(totalQuantity)
            })
            .catch(error => console.error('Error:', error));
            
        });
    });

    // Уменьшение количества товара
    document.querySelectorAll('.quantity-btn.decrease').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');
            const quantityElem = this.nextElementSibling;

            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                const newQuantity = data.cart[productId] || 0;

                // Обновляем количество товара
                quantityElem.textContent = newQuantity;

                // Если товара нет, скрываем панель управления количеством и показываем кнопку "Добавить в корзину"
                if (newQuantity === 0) {
                    const quantityControl = this.closest('.quantity-control');
                    quantityControl.style.display = 'none';
                    quantityControl.previousElementSibling.style.display = 'block';  // Показываем кнопку "Добавить в корзину"
                }
                const totalQuantity = Object.values(data.cart).reduce((total, quantity) => total + quantity, 0);
                console.log('totalQuantity', totalQuantity); // Вывод: 6
                updateCartCount(totalQuantity)
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Обработка кнопки удаления товара
    document.querySelectorAll('.remove-button').forEach(function(button) {
        button.addEventListener('click', function() {
            const plantId = this.getAttribute('data-plant-id');
            console.log('plantId', plantId);
            // Отправляем запрос на сервер для удаления товара из корзины
            fetch(`/delete_from_cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'  // Flask защита от CSRF-атак
                },
                body: JSON.stringify({
                    plant_id: plantId
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('data', data);
                if (data.success) {
                    // Удаляем товар из корзины на странице
                    location.href = location.href;
                } else {
                    alert('Произошла ошибка при удалении товара.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        });
    });
});