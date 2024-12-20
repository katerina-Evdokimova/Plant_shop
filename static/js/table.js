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
        headers.push(th.textContent.trim().split("\n")[0]);
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
// Загружаем данные таблицы для текущей страницы и текущего типа таблицы
async function loadTableData(page = 1, tableType = currentTableType, sortConfig = {}) {
    console.log("loadData");
    const params = new URLSearchParams();
    params.append('name', document.getElementById('data-table').dataset.tableType);
    params.append('page', page);

    // Добавляем параметры сортировки в URL
    Object.keys(sortConfig).forEach(columnIndex => {
        params.append(`sort_${columnIndex}`, sortConfig[columnIndex]);
    });

    const response = await fetch(`/api/table_data?${params.toString()}`);
    const data = await response.json();

    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    data.items.forEach(item => {
        console.log(item);
        const row = document.createElement('tr');

        // Перебираем данные по заголовкам
        getTableHeaders().forEach(header => {
            const cell = document.createElement('td');

            // Если колонка "Цена", "Количество" или "Скидка", делаем редактируемой
            if (["Цена", "Количество", "Скидка"].includes(header)) {
                cell.innerHTML = `<span class="editable-cell">${item[header] || ''}</span>`;
                cell.addEventListener('click', () => makeCellEditable(cell, header, item["id"]));
            } else if (header === "Роль") {
                cell.classList.add("role-cell");
                cell.innerHTML = generateRoleDropdown(item["Роль"], item["id"]);
            } else if (header === "Статус") {
                cell.innerHTML = generateStatusDropdown(item["Статус"], item["Номер заказа"]);
            } else {
                cell.textContent = item[header] || '';
            }
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });
}

function makeCellEditable(cell, fieldName, itemId) {
    // Проверяем, не редактируется ли уже эта ячейка
    if (cell.dataset.isEditing === "true") {
        return;
    }

    // Устанавливаем флаг редактирования
    cell.dataset.isEditing = "true";

    const currentValue = cell.textContent.trim();
    cell.innerHTML = `
        <input type="text" class="editable-input" value="${currentValue}">
        <button class="save-btn">✔</button>
        <button class="cancel-btn">✖</button>
    `;

    const input = cell.querySelector('.editable-input');
    const saveBtn = cell.querySelector('.save-btn');
    const cancelBtn = cell.querySelector('.cancel-btn');

    // Обработка сохранения
    saveBtn.addEventListener('click', () => saveEditedValue(input, fieldName, itemId, cell));
    // Обработка отмены
    cancelBtn.addEventListener('click', () => cancelEdit(cell, currentValue));
}

// Сохранение нового значения в ячейке
async function saveEditedValue(input, fieldName, itemId, cell) {
    const newValue = input.value.trim();
    if (newValue === '') {
        alert("Поле не может быть пустым!");
        return;
    }

    const response = await fetch('/api/update_item_field', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: itemId,
            field: fieldName,
            value: newValue
        })
    });

    if (response.ok) {
        alert("Данные успешно обновлены");
        cell.innerHTML = `<span class="editable-cell">${newValue}</span>`;
        cell.addEventListener('click', () => makeCellEditable(cell, fieldName, itemId));
    } else {
        alert("Ошибка при обновлении данных");
        cancelEdit(cell, input.defaultValue);
    }

    // Сбрасываем флаг редактирования
    cell.dataset.isEditing = "false";
}

// Отмена редактирования
function cancelEdit(cell, originalValue) {
    cell.innerHTML = `<span class="editable-cell">${originalValue}</span>`;
    cell.dataset.isEditing = "false"; // Сбрасываем флаг
}

// Генерация HTML для статуса с выпадающим списком
function generateStatusDropdown(currentStatus, orderId) {
    const statuses = ['обработка', 'одобрен', 'отклонен']; // Возможные статусы
    let html = `<select onchange="handleStatusChange(this.value, ${orderId})">`;

    statuses.forEach(status => {
        const selected = status === currentStatus ? 'selected' : '';
        html += `<option value="${status}" ${selected}>${status}</option>`;
    });

    html += `</select>`;
    return html;
}

// Обработка изменения статуса
async function handleStatusChange(newStatus, orderId) {
    if (confirm(`Вы уверены, что хотите изменить статус на "${newStatus}" у заказа "${orderId}"?`)) {
        const response = await fetch('/api/update_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orderId, newStatus })
        });

        if (response.ok) {
            alert("Статус успешно обновлён");
            loadTableData(currentPage, getTableType()); // Перезагружаем таблицу
        } else {
            alert("Ошибка при обновлении статуса");
        }
    }
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

function toggleRoleDropdown(dropdown) {
    const dropdownContent = dropdown.querySelector('.dropdown-content');
    dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
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
    // const detailTh = document.createElement('th');
    // detailTh.textContent = 'Подробнее';
    // tableHeader.appendChild(detailTh);
}

// Рендерим элементы пагинации
function renderPagination() {
    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';

    const buttonsToShow = []; // Массив для хранения кнопок, которые мы будем показывать

    // Определяем страницы для отображения
    if (totalPages <= 3) {
        // Если страниц меньше или равно 3, показываем все
        for (let i = 1; i <= totalPages; i++) {
            buttonsToShow.push(i);
        }
    } else {
        // Если текущая страница не на первой и не на последней, отображаем текущую, предшествующую и следующую
        if (currentPage === 1) {
            buttonsToShow.push(1, 2, 3); // Первые три страницы
        } else if (currentPage === totalPages) {
            buttonsToShow.push(totalPages - 2, totalPages - 1, totalPages); // Последние три страницы
        } else {
            buttonsToShow.push(currentPage - 1, currentPage, currentPage + 1); // Текущая и по одной рядом
        }
    }

    // Создаем кнопки для отображения
    buttonsToShow.forEach(i => {
        const button = document.createElement('button');
        button.textContent = i;
        button.classList.toggle('active', i === currentPage);
        button.addEventListener('click', () => goToPage(i));
        pageNumbers.appendChild(button);
    });

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


let sortConfig = {};  // Хранит текущую конфигурацию сортировки (колонка и направление)

// Функция для обработки клика по заголовку столбца
function handleColumnSort(columnIndex) {
    // Если для этого столбца сортировка не задана или была сброшена, сортируем по возрастанию
    if (!sortConfig[columnIndex]) {
        sortConfig[columnIndex] = 'asc';
    } else if (sortConfig[columnIndex] === 'asc') {
        // Если уже отсортировано по возрастанию, меняем на убывание
        sortConfig[columnIndex] = 'desc';
    } else {
        // Если уже отсортировано по убыванию, сбрасываем сортировку
        delete sortConfig[columnIndex];
    }

    // Обновляем иконки сортировки
    updateSortIcons();

    loadTableData(currentPage, getTableType(), sortConfig);  // Передаем конфигурацию сортировки в загрузку данных
}

// Обновление иконок стрелок
function updateSortIcons() {
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.textContent = '';  // Сбрасываем все стрелки
    });

    Object.keys(sortConfig).forEach(columnIndex => {
        const sortDirection = sortConfig[columnIndex];
        const icon = document.getElementById(`sort-icon-${columnIndex}`);
        icon.textContent = sortDirection === 'asc' ? '▲' : '▼';
        icon.style.visibility = 'visible';
    });
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    currentTableType = getTableType();
    fetchTotalPages(currentTableType);
    loadTableData(currentPage, currentTableType);
});
