// static/js/pagination.js

let currentPage = 1;
let totalPages = 1;

// Получаем заголовки колонок из таблицы
function getTableHeaders() {
    const headers = [];
    const thElements = document.querySelectorAll("thead th");
    thElements.forEach((th) => {
        headers.push(th.textContent.trim());
    });
    return headers;
}

// Загружаем общее количество страниц с сервера
async function fetchTotalPages() {
    const response = await fetch('/api/total_pages');
    const data = await response.json();
    totalPages = data.total_pages;
    renderPagination();
}

// Загружаем данные таблицы для текущей страницы
async function loadTableData(page = 1) {
    const headers = getTableHeaders();
    const response = await fetch(`/api/table_data?page=${page}`);
    const data = await response.json();

    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    data.items.forEach(item => {
        const row = document.createElement('tr');

        headers.forEach(header => {
            if (header !== 'Подробнее') {
                const cell = document.createElement('td');
                cell.textContent = item[header] || '';
                row.appendChild(cell);
            }
        });

        const linkCell = document.createElement('td');
        const link = document.createElement('a');
        link.href = item.href;
        link.textContent = 'Перейти';
        linkCell.appendChild(link);
        row.appendChild(linkCell);

        tableBody.appendChild(row);
    });
}

// Рендерим элементы пагинации
function renderPagination() {
    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.classList.toggle('active', i === currentPage);
        button.addEventListener('click', () => goToPage(i));
        pageNumbers.appendChild(button);
    }

    document.getElementById('prevButton').disabled = currentPage <= 1;
    document.getElementById('nextButton').disabled = currentPage >= totalPages;
}

// Переход на конкретную страницу
function goToPage(page) {
    currentPage = page;
    loadTableData(page);
    renderPagination();
}

// Обработка кнопок "Назад" и "Далее"
function changePage(direction) {
    if (direction === 'next' && currentPage < totalPages) {
        goToPage(currentPage + 1);
    } else if (direction === 'prev' && currentPage > 1) {
        goToPage(currentPage - 1);
    }
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    fetchTotalPages();
    loadTableData(currentPage);
});