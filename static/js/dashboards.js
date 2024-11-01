
// Функция для круговой диаграммы
function loadProductData() {
    $.getJSON('/api/product_data', function(data) {
        new Chart(document.getElementById('productChart'), {
            type: 'pie',
            data: {
                labels: ['В наличии', 'Закончились'],
                datasets: [{
                    label: 'Растения',
                    data: [data.total - data.out_of_stock, data.out_of_stock],
                    backgroundColor: ['#4CAF50', '#D23A01']
                }]
            }
        });
    });
}

// Функция для столбчатой диаграммы
function loadUserData() {
    $.getJSON('/api/user_data', function(data) {
        new Chart(document.getElementById('userChart'), {
            type: 'bar',
            data: {
                labels: ['Suppliers', 'Sellers', 'Clients'],
                datasets: [{
                    label: 'Users',
                    data: [data.suppliers, data.sellers, data.clients],
                    backgroundColor: ['#3e95cd', '#8e5ea2', '#3cba9f']
                }]
            }
        });
    });
}

// Функция для отображения статусов заказов
function loadOrderStatuses() {
    $.getJSON('/api/order_statuses', function(data) {
        new Chart(document.getElementById('orderChart'), {
            type: 'doughnut',
            data: {
                labels: ['Обработка', 'Обработан', 'Отменен'],
                datasets: [{
                    label: 'Статус заказа',
                    data: [data.processing, data.approved, data.error],
                    backgroundColor: ['#FFC107', '#28A745', '#D23A01']
                }]
            }
        });
    });
}

// Функция для отображения последних действий
function loadRecentActivity() {
    $.getJSON('/api/recent_activity', function(data) {
        const list = data.map(item => `<li>Order #${item.id} - ${item.status} - ${item.date}</li>`);
        $('#recentActivity').html(list.join(''));
    });
}

// Функция для отображения популярных товаров
// Функция для отображения популярных товаров с карточками
function loadTopProducts() {
    $.getJSON('/api/top_products', function(data) {
        const productCards = data.map(item => `
            <div class="col-12 col-md-4 mb-4">
                <div class="card">
                    <img src="/static/${item.image}" class="card-img-top" alt="${item.name}">
                    <div class="card-body text-center">
                        <h6 class="card-title">${item.name}</h6>
                        <p class="text-muted">${item.category}</p>
                        <a href="/plant/${item.id}" class="button-user">Посмотреть</a>
                    </div>
                </div>
            </div>
        `);
        $('#topProducts').html(productCards.join(''));
    });
}

// Загрузка всех данных при загрузке страницы
$(document).ready(function() {
    loadProductData();
    loadUserData();
    loadOrderStatuses();
    loadRecentActivity();
    loadTopProducts();
});
