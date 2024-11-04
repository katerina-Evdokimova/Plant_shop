let currentPage = 1;
let totalPages = 1;
let currentTableType = 'plants';  // Задайте тип таблицы, например, 'plants', 'users', 'orders'

// Получаем тип таблицы из HTML (если у вас одна таблица, можно задавать напрямую)
function getTableType() {
    const table = document.getElementById('data-table');
    return table.getAttribute('data-table-type') || currentTableType;
}

// Получаем заголовки колонок из таблицы
function getTableHeaders() {
    const headers = [];
    const thElements = document.querySelectorAll("thead th");
    thElements.forEach((th) => {
        headers.push(th.textContent.trim());
    });
    return headers;
}

// Обновляем общее количество страниц, указывая тип таблицы
async function fetchTotalPages(tableType) {
    const response = await fetch(`/api/total_pages?name=${tableType}`);
    const data = await response.json();
    totalPages = data.total_pages;
    renderPagination();
}

// Загружаем данные таблицы для текущей страницы и текущего типа таблицы
// Загрузка данных таблицы
async function loadTableData(page = 1, tableType = currentTableType) {
    const response = await fetch(`/api/table_data?name=${tableType}&page=${page}`);
    const data = await response.json();
    
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    data.items.forEach(item => {
        const row = document.createElement('tr');

        // Перебираем данные по заголовкам
        getTableHeaders().forEach(header => {
            const cell = document.createElement('td');

            if (header === "Роль") {
                cell.classList.add("role-cell");
                cell.innerHTML = generateRoleDropdown(item["Роль"], item["id"]);
            }else if (header == "Подробнее"){
           
                const linkCell = document.createElement('td');
                const link = document.createElement('a');
                link.href = item.href;
                link.textContent = 'Перейти';
                linkCell.appendChild(link);
                row.appendChild(linkCell);
            }
             else {
                cell.textContent = item[header] || '';
            }
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });
}

// Генерация HTML для выпадающего списка с ролями
function generateRoleDropdown(roles, userId) {
    const availableRoles = ["Админ", "Клиент", "Поставщик", "Продавец"]; // Доступные роли
    let html = `<div class="role-dropdown" onclick="toggleRoleDropdown(this)">
                  <span class="role-list">${roles.join(", ")}</span>
                  <div class="dropdown-content" style="display: none;">`;

    availableRoles.forEach(role => {

        const checked = roles.includes(role) ? "checked" : "";
        html += `<label><input type="checkbox" ${checked} onclick="handleRoleChange(event, '${role}', ${userId})"> ${role}</label>`;
    });

    html += `</div></div>`;
    return html;
}

// Показ или скрытие выпадающего списка ролей
function toggleRoleDropdown(dropdown) {
    const content = dropdown.querySelector(".dropdown-content");
    content.style.display = content.style.display === "none" ? "block" : "none";
}

// Обработка изменения роли пользователя
function handleRoleChange(event, role, userId) {
    event.stopPropagation();
    const isAdding = event.target.checked;
    const action = isAdding ? "добавить" : "удалить";

    if (confirm(`Вы уверены, что хотите ${action} роль "${role}" для этого пользователя?`)) {
        updateRole(userId, role, isAdding);
    } else {
        event.target.checked = !isAdding; // Отмена действия, если пользователь не подтвердил
    }
}

// API-запрос для обновления роли
async function updateRole(userId, role, isAdding) {
    const response = await fetch('/api/update_role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, role, isAdding })
    });

    if (response.ok) {
        alert("Роль успешно обновлена");
        loadTableData(currentPage, getTableType());  // Обновление данных таблицы
    } else {
        alert("Ошибка при обновлении роли");
    }
}

// Обновление заголовков таблицы
function updateTableHeaders(headers) {
    const tableHeader = document.querySelector('thead tr');
    tableHeader.innerHTML = '';

    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        tableHeader.appendChild(th);
    });

    // Добавляем колонку для кнопки перехода
    const detailTh = document.createElement('th');
    detailTh.textContent = 'Подробнее';
    tableHeader.appendChild(detailTh);
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
    loadTableData(page, getTableType());
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
    currentTableType = getTableType();
    fetchTotalPages(currentTableType);
    loadTableData(currentPage, currentTableType);
});