document.addEventListener('DOMContentLoaded', function () {
    // Добавление товара в корзину
    document.querySelectorAll('.add-to-cart').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');

            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                // Обновляем интерфейс
                this.style.display = 'none';
                const quantityControl = this.nextElementSibling;
                quantityControl.style.display = 'block';
                quantityControl.querySelector('.quantity').textContent = data.cart[productId];
            });
        });
    });

    // Увеличение количества товара
    document.querySelectorAll('.quantity-btn.increase').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');

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
                this.previousElementSibling.textContent = data.cart[productId];
            });
        });
    });

    // Уменьшение количества товара
    document.querySelectorAll('.quantity-btn.decrease').forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-plant-id');

            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                // Обновляем количество товара
                const quantityElem = this.nextElementSibling;
                const newQuantity = data.cart[productId] || 0;

                quantityElem.textContent = newQuantity;

                // Если товара нет, скрываем управление количеством
                if (newQuantity === 0) {
                    const quantityControl = this.closest('.quantity-control');
                    quantityControl.style.display = 'none';
                    quantityControl.previousElementSibling.style.display = 'block';  // Показать кнопку "Добавить"
                }
            });
        });
    });
});