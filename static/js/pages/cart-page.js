// ===== ОБНОВЛЕНИЕ КОЛИЧЕСТВА =====
async function updateQuantity(productId, change, manualValue = null) {
    const input = document.getElementById(`qty-input-${productId}`);

    // Вычисляем новое количество
    let newQty = manualValue !== null ? parseInt(manualValue) : parseInt(input.value) + change;
    if (newQty < 1) removeFromCart(productId);

    // Визуально сразу меняем цифру (чтобы не ждать ответа сервера)
    input.value = newQty;

    try {
        const response = await fetch(`/api/cart/update/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ quantity: newQty })
        });

        const data = await response.json();

        if (data.success) {
            // Обновляем сумму ЭТОГО товара
            const itemTotalEl = document.getElementById(`item-total-${productId}`);
            if (itemTotalEl) itemTotalEl.textContent = data.item_total + ' ₽';

            // Обновляем общие суммы
            updateSummary(data.cart_total, data.cart_count);
        } else {
            alert('Ошибка: ' + (data.error || 'Не удалось обновить количество'));
            location.reload(); // При ошибке перезагружаем
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка соединения с сервером');
        location.reload();
    }
}

// ===== УДАЛЕНИЕ ТОВАРА =====
async function removeFromCart(productId) {
    // if (!confirm('Удалить этот товар из корзины?')) return;

    const itemRow = document.getElementById(`cart-item-${productId}`);
    if (!itemRow) return;

    // 1. Визуально скрываем товар (анимация)
    itemRow.style.transition = 'all 0.3s ease';
    itemRow.style.opacity = '0';
    itemRow.style.transform = 'translateX(-20px)';

    try {
        const response = await fetch(`/api/cart/remove/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            // 2. Ждем окончания анимации и удаляем из DOM
            setTimeout(() => {
                itemRow.remove();

                // 3. Обновляем итоги
                updateSummary(data.cart_total, data.cart_count);

                // 4. Если товаров больше нет — перезагружаем страницу (покажем "Корзина пуста")
                const remainingItems = document.querySelectorAll('.cart-item');
                if (remainingItems.length === 0) {
                    setTimeout(() => location.reload(), 500);
                }
            }, 300);
        } else {
            alert('Ошибка при удалении');
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка соединения');
        location.reload();
    }
}

// ===== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: Обновление итогов =====
function updateSummary(total, count) {
    // Обновляем суммы в блоке "Итого"
    const totalEls = document.querySelectorAll('#summary-total, #final-total');
    totalEls.forEach(el => {
        if (el) el.textContent = total + ' ₽';
    });

    // Обновляем счетчик товаров (текст "Товаров: N")
    const countEl = document.getElementById('summary-count');
    if (countEl) countEl.textContent = count;

    // Обновляем красный кружок в шапке (плавающая кнопка и меню)
    const cartCounters = document.querySelectorAll('.cart-count');
    cartCounters.forEach(counter => {
        if (counter) counter.textContent = count;
    });
}

// ===== CSRF Token =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}