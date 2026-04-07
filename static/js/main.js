function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i += 1) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const iconMap = {
        success: 'check-circle',
        warning: 'exclamation-triangle',
        error: 'times-circle',
        info: 'info-circle',
    };

    notification.innerHTML = `
        <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    requestAnimationFrame(() => {
        notification.classList.add('show');
    });

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

async function loadCartItems() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const cartCount = document.querySelector('.cart-count');

    if (!cartItems || !cartTotal) return;

    try {
        const response = await fetch('/api/cart/items/');
        const data = await response.json();

        if (!data.items || data.items.length === 0) {
            cartItems.innerHTML = '<p class="empty-cart">Корзина пуста</p>';
        } else {
            let html = '';

            data.items.forEach((item) => {
                html += `
                    <div class="cart-sidebar-item">
                        <div class="item-info">
                            <h4>${item.product_name}</h4>
                            <p>${item.quantity} шт. × ${item.price} ₽</p>
                        </div>
                        <div class="item-actions">
                            <button type="button" class="btn-sm" onclick="changeCartQuantity(${item.product_id}, -1)">-</button>
                            <span>${item.quantity}</span>
                            <button type="button" class="btn-sm" onclick="changeCartQuantity(${item.product_id}, 1)">+</button>
                            <button type="button" class="btn-remove" onclick="removeFromCart(${item.product_id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });

            cartItems.innerHTML = html;
        }

        cartTotal.textContent = `${data.total} ₽`;

        if (cartCount) {
            cartCount.textContent = data.count;
        }
    } catch (error) {
        console.error(error);
        showNotification('Не удалось загрузить корзину', 'error');
    }
}

function toggleCartSidebar(forceOpen = null) {
    const sidebar = document.getElementById('cartSidebar');
    if (!sidebar) return;

    if (forceOpen === true) {
        sidebar.classList.add('active');
    } else if (forceOpen === false) {
        sidebar.classList.remove('active');
    } else {
        sidebar.classList.toggle('active');
    }

    if (sidebar.classList.contains('active')) {
        loadCartItems();
    }
}

async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch(`/api/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity }),
        });

        const data = await response.json();

        if (data.success) {
            updateCartCount(data.cart_count);
            showNotification(data.message || 'Товар добавлен в корзину', 'success');
            loadCartItems();
        } else {
            showNotification(data.error || 'Ошибка при добавлении', 'error');
        }
    } catch (error) {
        console.error(error);
        showNotification('Ошибка при добавлении в корзину', 'error');
    }
}

async function removeFromCart(productId) {
    try {
        const response = await fetch(`/api/cart/remove/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        const data = await response.json();

        if (data.success) {
            updateCartCount(data.cart_count || 0);
            loadCartItems();
            showNotification('Товар удалён из корзины', 'success');
        } else {
            showNotification(data.error || 'Ошибка удаления', 'error');
        }
    } catch (error) {
        console.error(error);
        showNotification('Ошибка удаления', 'error');
    }
}

async function changeCartQuantity(productId, change) {
    try {
        const countElement = document.querySelector('.cart-count');
        const currentCount = countElement ? parseInt(countElement.textContent || '0', 10) : 0;

        const response = await fetch(`/api/cart/update/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quantity: Math.max(1, currentCount + change),
            }),
        });

        const data = await response.json();

        if (data.success) {
            updateCartCount(data.cart_count);
            loadCartItems();
        } else {
            showNotification(data.error || 'Ошибка обновления количества', 'warning');
        }
    } catch (error) {
        console.error(error);
        showNotification('Ошибка обновления корзины', 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('floatingCartBtn');
    const closeBtn = document.getElementById('closeCartSidebarBtn');
    const sidebar = document.getElementById('cartSidebar');

    if (openBtn) {
        openBtn.addEventListener('click', () => toggleCartSidebar());
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => toggleCartSidebar(false));
    }

    document.addEventListener('click', (event) => {
        if (!sidebar || !sidebar.classList.contains('active')) return;

        const clickedInsideSidebar = sidebar.contains(event.target);
        const clickedOpenBtn = openBtn && openBtn.contains(event.target);

        if (!clickedInsideSidebar && !clickedOpenBtn) {
            toggleCartSidebar(false);
        }
    });
});