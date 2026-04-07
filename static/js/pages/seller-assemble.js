let isScanning = false;
let lastScanTime = 0;
const SCAN_DEBOUNCE = 2000;
let addedProducts = new Set();

const articleInput = document.getElementById('articleInput');

async function scanArticle() {
    if (isScanning) return;
    const article = articleInput?.value.trim();
    if (!article) { alert('Введите артикул!'); return; }

    isScanning = true;
    lastScanTime = Date.now();
    const resultDiv = document.getElementById('scanResult');
    resultDiv.style.display = 'block';
    resultDiv.className = 'scan-result';
    resultDiv.innerHTML = '<div style="padding:30px;text-align:center">🔍 Поиск...</div>';
    articleInput.value = '';
    articleInput.disabled = true;

    try {
        const response = await fetch(`/api/product-by-article/?article=${encodeURIComponent(article)}`);
        const data = await response.json();

        if (data.success) {
            const p = data.product;
            const isAdded = addedProducts.has(p.id);
            resultDiv.className = 'scan-result success';
            resultDiv.innerHTML = `
                <div class="scan-result-content">
                    <div class="scan-result-image">${p.image ? `<img src="${p.image}" alt="">` : '<div style="height:100%;display:flex;align-items:center;justify-content:center;font-size:60px;color:#ccc">📦</div>'}</div>
                    <div class="scan-result-info">
                        <h3>${p.name}</h3>
                        <p class="article">${p.article}</p>
                        <p><strong>На складе:</strong> ${p.quantity} шт.</p>
                    </div>
                    <div class="scan-result-actions">
                        ${isAdded ? '<span class="btn btn-outline" style="cursor:default">✓ Уже добавлено</span>' : `<button class="btn btn-success" onclick="addScannedItem(${p.id})">Добавить</button>`}
                    </div>
                </div>`;
        } else {
            resultDiv.className = 'scan-result error';
            resultDiv.innerHTML = `<div style="padding:30px;text-align:center;color:#c0392b">❌ ${data.error || 'Не найдено'}</div>`;
        }
    } catch (e) {
        resultDiv.className = 'scan-result error';
        resultDiv.innerHTML = '<div style="padding:30px;text-align:center;color:#c0392b">❌ Ошибка</div>';
    } finally {
        isScanning = false;
        articleInput.disabled = false;
        articleInput.focus();
    }
}

async function addScannedItem(productId) {
    if (isScanning) return;
    isScanning = true;
    try {
        const response = await fetch(`/api/order/${window.ORDER_UUID}/add-item/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        const data = await response.json();
        if (data.success) {
            addedProducts.add(productId);
            addToAssembledList(data.item);
            document.getElementById('scanResult').style.display = 'none';
            articleInput.value = '';
        } else {
            alert('❌ ' + data.error);
        }
    } catch (e) { alert('Ошибка'); } finally { isScanning = false; }
}

async function quickAdd(productId, quantity) {
    if (addedProducts.has(productId)) { alert('Уже добавлено!'); return; }
    try {
        const response = await fetch(`/api/order/${window.ORDER_UUID}/add-item/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        });
        const data = await response.json();
        if (data.success) {
            addedProducts.add(productId);
            addToAssembledList(data.item);
        } else { alert('❌ ' + data.error); }
    } catch (e) { alert('Ошибка'); }
}

function addToAssembledList(item) {
    const container = document.getElementById('assembledContainer');
    container.insertAdjacentHTML('beforeend', `<div class="assembled-item"><div><strong>${item.name}</strong><br><small>${item.article}</small></div><strong>${item.price} ₽</strong></div>`);
}

function finishAssembly() {
    if (!confirm('Завершить сборку?')) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/seller/assemble/${window.ORDER_UUID}/finish/`;
    form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">`;
    document.body.appendChild(form);
    form.submit();
}

function getCookie(name) {
    let value = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(c => {
            c = c.trim();
            if (c.startsWith(name + '=')) value = decodeURIComponent(c.substring(name.length + 1));
        });
    }
    return value;
}