(function() {
    // 1. Intercepteur pour capturer les données de l'API dès qu'elles arrivent
    const ordersMap = new Map();
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener('load', function() {
            try {
                const data = JSON.parse(this.responseText);
                // Si c'est une liste de commandes ou une commande unique
                const items = Array.isArray(data) ? data : (data.result && data.result.orders ? data.result.orders : [data]);
                items.forEach(order => {
                    if (order.id) ordersMap.set(String(order.id), order);
                });
            } catch (e) {}
        });
        originalOpen.apply(this, arguments);
    };

    function formatNumber(num) {
        return parseFloat(num).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$& ') + " Da";
    }

    // 2. Fonction d'injection dans le DOM
    function injectValues() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            if (table.querySelector('.valeur-calculee')) return;

            // Trouver l'ID de la commande dans le texte de la carte
            const card = table.closest('.p-4'); // Cherche le container parent
            if (!card) return;
            
            const idMatch = card.innerText.match(/N°\s*(\d+)/);
            if (!idMatch) return;
            
            const orderId = idMatch[1];
            const orderData = ordersMap.get(orderId);

            if (orderData && orderData.valeur_net !== undefined) {
                const rows = table.querySelectorAll('tr');
                let insertionPoint = null;

                // On cherche la ligne "Observation" pour insérer juste AVANT
                rows.forEach(tr => {
                    if (tr.innerText.includes('Observation')) insertionPoint = tr;
                });

                if (insertionPoint) {
                    const html = `
                        <tr class="valeur-calculee">
                            <td class="border border-gray-500 p-2">Valeur net</td>
                            <td class="border border-gray-500 p-2" style="font-weight:bold; color:#f39c12;">${formatNumber(orderData.valeur_net)}</td>
                        </tr>
                        <tr class="valeur-calculee">
                            <td class="border border-gray-500 p-2">Valeur brute</td>
                            <td class="border border-gray-500 p-2" style="font-weight:bold; color:#2ca030;">${formatNumber(orderData.valeur_brute)}</td>
                        </tr>
                    `;
                    insertionPoint.insertAdjacentHTML('beforebegin', html);
                }
            }
        });
    }

    // 3. Observer les changements (React est dynamique)
    const observer = new MutationObserver(injectValues);
    observer.observe(document.body, { childList: true, subtree: true });
})();