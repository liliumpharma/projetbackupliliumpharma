(function () {
    const CONFIG = {
        cardClass: ".p-4.rounded.bg-slate-700.mb-3.w-full",
        checkboxClass: ".PrivateSwitchBase-input.css-1m9pwf3"
    };

    function determineType(text) {
        const hasSuper = text.includes("Super Grossiste");
        const hasPharma = text.includes("Pharmacie");
        const totalGrosCount = (text.match(/Grossiste/g) || []).length;
        const superGrosCount = (text.match(/Super Grossiste/g) || []).length;
        const hasGros = totalGrosCount > superGrosCount;

        if (hasSuper) {
            if (hasPharma || hasGros) return "GROS_SUPER";
            return "OFFICE";
        }
        if (hasPharma && hasGros) return "PH_GROS";
        return "OTHER";
    }

    function applyFilters() {
        const officeActive = document.getElementById('custom-filter-office').checked;
        const grosSuperActive = document.getElementById('custom-filter-gros-super').checked;
        const phGrosActive = document.getElementById('custom-filter-ph-gros').checked;

        const cards = document.querySelectorAll(CONFIG.cardClass);
        
        cards.forEach(card => {
            const text = card.innerText || "";
            const type = determineType(text);
            const noFiltersSelected = !officeActive && !grosSuperActive && !phGrosActive;
            
            if (noFiltersSelected) {
                card.style.display = "block";
            } else {
                const showOffice = officeActive && type === "OFFICE";
                const showGrosSuper = grosSuperActive && type === "GROS_SUPER";
                const showPhGros = phGrosActive && type === "PH_GROS";
                card.style.display = (showOffice || showGrosSuper || showPhGros) ? "block" : "none";
            }
        });
    }

    function injectCheckboxes() {
        const existingCheckboxes = document.querySelectorAll(CONFIG.checkboxClass);
        if (existingCheckboxes.length === 0) {
            setTimeout(injectCheckboxes, 1000);
            return;
        }

        if (document.getElementById('custom-filter-wrapper')) return;

        const parent = existingCheckboxes[0].closest('div');
        const wrapper = document.createElement('div');
        wrapper.id = 'custom-filter-wrapper';

        // STYLING: Added translateY to move the filters lower and align them with the buttons
        wrapper.style.cssText = `
            display: flex; 
            gap: 18px; 
            margin-left: 20px; 
            color: white; 
            font-size: 13px; 
            align-items: center; 
            background: #1e293b; 
            padding: 6px 14px; 
            border-radius: 6px; 
            border: 1px solid #334155;
            transform: translateY(6px); 
            user-select: none;
        `;
        
        wrapper.innerHTML = `
            <label style="cursor:pointer; display:flex; align-items:center; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                <input type="checkbox" id="custom-filter-office" style="margin-right:6px; cursor:pointer; width:16px; height:16px;"> Office Lilium
            </label>
            <label style="cursor:pointer; display:flex; align-items:center; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                <input type="checkbox" id="custom-filter-gros-super" style="margin-right:6px; cursor:pointer; width:16px; height:16px;"> GROS_SUPER
            </label>
            <label style="cursor:pointer; display:flex; align-items:center; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                <input type="checkbox" id="custom-filter-ph-gros" style="margin-right:6px; cursor:pointer; width:16px; height:16px;"> PH_GROS
            </label>
        `;

        parent.appendChild(wrapper);

        ['custom-filter-office', 'custom-filter-gros-super', 'custom-filter-ph-gros'].forEach(id => {
            document.getElementById(id).addEventListener('change', applyFilters);
        });
    }

    if (document.readyState === 'complete') injectCheckboxes();
    else window.addEventListener('load', injectCheckboxes);
})();