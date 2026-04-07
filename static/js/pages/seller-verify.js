async function verifyOrder() {
    const orderQr = document.getElementById('orderQr').value.trim();
    const packageQr = document.getElementById('packageQr').value.trim();
    const resultDiv = document.getElementById('verifyResult');

    if (!orderQr || !packageQr) {
        showNotification('Введите оба QR-кода', 'warning');
        return;
    }

    try {
        const response = await fetch('/store/api/scan-verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                order_qr: orderQr,
                package_qr: packageQr,
            }),
        });

        const data = await response.json();

        resultDiv.style.display = 'block';

        if (data.status === 'success') {
            resultDiv.className = 'verify-result success';
            resultDiv.innerHTML = `
                <i class="fas fa-check-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                <h3>${data.message}</h3>
                <p>Клиент: ${data.client}</p>
                <p>Сумма: ${data.total} ₽</p>
            `;
        } else {
            resultDiv.className = 'verify-result error';
            resultDiv.innerHTML = `
                <i class="fas fa-times-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                <h3>${data.message}</h3>
            `;
        }
    } catch (error) {
        console.error(error);
        showNotification('Ошибка проверки QR', 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('verifyOrderBtn');
    const orderInput = document.getElementById('orderQr');
    const packageInput = document.getElementById('packageQr');

    if (btn) {
        btn.addEventListener('click', verifyOrder);
    }

    if (orderInput) {
        orderInput.focus();
    }

    [orderInput, packageInput].forEach((input) => {
        if (!input) return;
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                verifyOrder();
            }
        });
    });
});