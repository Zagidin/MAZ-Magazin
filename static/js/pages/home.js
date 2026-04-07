function openProductModal(productId) {
    const modal = document.getElementById('productModal');
    const content = document.getElementById('productModalContent');

    if (!modal || !content) return;

    modal.classList.add('active');
    content.innerHTML = '<p>Загрузка...</p>';

    fetch(`/api/product/${productId}/`)
        .then((response) => response.json())
        .then((data) => {
            content.innerHTML = data.html || '<p>Товар не найден</p>';
        })
        .catch((error) => {
            console.error(error);
            content.innerHTML = '<p>Ошибка загрузки товара</p>';
        });
}

function closeProductModal() {
    const modal = document.getElementById('productModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function openQrModal(orderUuid) {
    const modal = document.getElementById('qrModal');
    const img = document.getElementById('qrModalImage');

    if (!modal || !img) return;

    img.src = `/api/qr/order/${orderUuid}/`;
    modal.style.display = 'flex';
}

function closeQrModal() {
    const modal = document.getElementById('qrModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

window.openProductModal = openProductModal;
window.closeProductModal = closeProductModal;
window.openQrModal = openQrModal;
window.closeQrModal = closeQrModal;