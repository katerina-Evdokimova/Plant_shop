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
// Показать или скрыть выпадающее меню
        document.getElementById('account-button').addEventListener('click', function() {
            var dropdown = document.getElementById('dropdown-menu');
            console.log("+++", dropdown)
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
            console.log("ff+")
        });

        document.addEventListener('click', function(event) {
            // Проверяем, был ли клик на элементе внутри контейнера
            const iconContainer = document.querySelector('.icon-container');
            if (!iconContainer.contains(event.target)) {
                console.log('Клик произошел вне объекта.');
                var dropdown = document.getElementById('dropdown-menu');
                dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
                console.log("ff+")
            }
        });
        
    
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

    document.getElementById('load-more').addEventListener('click', function() {
        let currentCount = document.querySelectorAll('.product-card').length + document.querySelectorAll('.product-card-none').length;
    
        fetch('/load-more-products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ n: currentCount })
        })
        .then(response => response.json())
        .then(data => {
            // Вставляем новые продукты в раздел с товарами
            document.querySelector('.proposals-section').insertAdjacentHTML('beforeend', data.templates);
            // Проверяем, есть ли еще товары
            if (data.has_more) {
                document.getElementById('load-more').style.display = 'none'; // Скрыть кнопку
            }
        })
        .catch(error => console.error('Error:', error));
    });

    document.querySelectorAll('.filter-dropdown a').forEach(function(sortLink) {
        sortLink.addEventListener('click', function(event) {
            event.preventDefault();  // Отменяем переход по ссылке
    
            const sortParam = this.getAttribute('href').split('=')[1];  // Получаем значение сортировки (asc или desc)
    
            // Асинхронный запрос для получения отсортированных товаров
            fetch(`/catalog/sort?sort=${sortParam}`,
                {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ n: document.querySelectorAll('.product-card').length + document.querySelectorAll('.product-card-none').length })
            })
                .then(response => response.json())  // Получаем HTML с товарами
                .then(data => {
                    console.log("!!!data", data)
                    // Обновляем содержимое секции товаров
                    document.querySelector('.proposals-section').innerHTML = data.templates;
                    console.log("done")
                    // Обновляем стрелку сортировки
                    const sortArrow = document.getElementById('sort-arrow');
                    sortArrow.classList.remove('asc', 'desc');
                    if (sortParam === 'asc') {
                        sortArrow.classList.add('asc');
                    } else if (sortParam === 'desc') {
                        sortArrow.classList.add('desc');
                    }
                })
                .catch(error => console.error('Ошибка при загрузке товаров:', error));
        });
    });


    // Показать или скрыть выпадающее меню
    document.getElementById('filter-button').addEventListener('click', function() {
        var dropdown = document.getElementById('filter-dropdown');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });

    // Закрытие меню при клике вне фильтра
    window.onclick = function(event) {
        if (!event.target.matches('.filter-button')) {
            var dropdowns = document.getElementsByClassName("filter-dropdown");
            for (var i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.style.display === "block") {
                    openDropdown.style.display = "none";
                }
            }
        }
    };
});
