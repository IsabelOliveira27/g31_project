function initAutocomplete(inputId, boxId, selectId, apiUrl) {
    const searchInput = document.getElementById(inputId);
    const suggestionBox = document.getElementById(boxId);
    const selectAttr = document.getElementById(selectId);

    if (!searchInput || !suggestionBox || !selectAttr) return;

    let validSuggestions = [];

    searchInput.addEventListener('input', function(e) {
        const text = e.target.value.trim();
        const attribute = selectAttr.value;
        
        if (text.length >= 1) {
            const url = apiUrl + '?att=' + attribute + '&val=' + encodeURIComponent(text);
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    suggestionBox.innerHTML = '';
                    validSuggestions = data.map(item => item.texto.toString().toLowerCase());
                    
                    if (data && data.length > 0) {
                        suggestionBox.style.display = 'block';
                        suggestionBox.style.background = '#ffffff';
                        suggestionBox.style.border = '1px solid #cbd5e1';
                        suggestionBox.style.position = 'absolute';
                        suggestionBox.style.width = '100%';
                        suggestionBox.style.zIndex = '9999';
                        
                        data.forEach(item => {
                            const div = document.createElement('div');
                            div.style.padding = '8px';
                            div.style.cursor = 'pointer';
                            div.style.borderBottom = '1px solid #f1f5f9';
                            div.style.color = '#334155';
                            div.style.display = 'flex';
                            div.style.justifyContent = 'space-between';
                            
                            div.innerHTML = '<span>üîç ' + item.texto + '</span><small style="color:#94a3b8">' + item.qtd + ' registo(s)</small>';
                            
                            div.addEventListener('click', function() {
                                searchInput.value = item.texto;
                                suggestionBox.style.display = 'none';
                                searchInput.form.submit();
                            });
                            
                            suggestionBox.appendChild(div);
                        });
                    } else {
                        suggestionBox.style.display = 'none';
                    }
                })
                .catch(err => console.error(err));
        } else {
            suggestionBox.style.display = 'none';
            validSuggestions = [];
        }
    });

    if (searchInput.form) {
        searchInput.form.addEventListener('submit', function(e) {
            const text = searchInput.value.trim();
            const attribute = selectAttr.value;
            let labelText = selectAttr.options[selectAttr.selectedIndex].text;

            labelText = labelText.toLowerCase().replace(/\bid\b/g, 'ID');
            labelText = labelText.split(' ').map(w => w === 'de' || w === 'do' || w === 'da' ? w : w === 'ID' ? 'ID' : w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

            if (attribute === 'id' || attribute.endsWith('_id')) {
                if (text.length > 0 && validSuggestions.length > 0 && !validSuggestions.includes(text.toLowerCase())) {
                    e.preventDefault();
                    alert("O " + labelText + " '" + text + "' n√£o existe no sistema!");
                }
            }
        });
    }

    document.addEventListener('click', function(e) {
        if (e.target !== searchInput && !suggestionBox.contains(e.target)) {
            suggestionBox.style.display = 'none';
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll("a");
    links.forEach(link => {
        const button = link.querySelector("button");
        if (button && button.hasAttribute("disabled")) {
            link.addEventListener("click", function (e) {
                e.preventDefault();
            });
        }
    });

    const forms = document.querySelectorAll("form[action*='option=save']");
    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const gclassInput = form.querySelector("input[name='gclass_string']");
            if (gclassInput && gclassInput.value.trim() !== "") {
                const parts = gclassInput.value.split(";");
                const stringId = parseInt(parts[0], 10);
                if (!isNaN(stringId) && stringId < 0) {
                    e.preventDefault();
                    alert("O ID '" + parts[0] + "' n√£o √© v√°lido ou n√£o pertence a um grupo existente!");
                    return;
                }
            }

            const idInputs = form.querySelectorAll("input[name*='id'], input[name='type']");
            for (let input of idInputs) {
                if (input.disabled || input.readOnly) continue;
                
                const val = parseInt(input.value.trim(), 10);
                if (!isNaN(val) && val < 0) {
                    let labelText = "";
                    let container = input.parentElement;
                    
                    while (container && container !== form) {
                        const label = container.querySelector('label');
                        if (label) {
                            labelText = label.innerText.replace(':', '').trim();
                            break;
                        }
                        container = container.parentElement;
                    }
                    
                    if (!labelText) {
                        if (input.name === "equipment_id") labelText = "ID do Equipamento";
                        else if (input.name === "operator_id") labelText = "ID do Operador";
                        else if (input.name === "type") labelText = "Tipo";
                        else labelText = "ID";
                    } else {
                        labelText = labelText.toLowerCase().replace(/\bid\b/g, 'ID');
                        labelText = labelText.split(' ').map(w => w === 'de' || w === 'do' || w === 'da' ? w : w === 'ID' ? 'ID' : w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                    }
                    
                    e.preventDefault();
                    alert("O " + labelText + " '" + input.value + "' n√£o pertence a um grupo existente!");
                    return;
                }
            }
        });
    });

    if (document.getElementById("equipment_search_val")) {
        initAutocomplete("equipment_search_val", "equipment_autocomplete_box", "equipment_search_att", "/api/suggest_equipments");
    }
    if (document.getElementById("operator_search_val")) {
        initAutocomplete("operator_search_val", "operator_autocomplete_box", "operator_search_att", "/api/suggest_operators");
    }
    if (document.getElementById("utilization_search_val")) {
        initAutocomplete("utilization_search_val", "utilization_autocomplete_box", "utilization_search_att", "/api/suggest_utilization");
    }
    if (document.getElementById("maintenance_search_val")) {
        initAutocomplete("maintenance_search_val", "maintenance_autocomplete_box", "maintenance_search_att", "/api/suggest_maintenance");
    }
    if (document.getElementById("mtypes_search_val")) {
        initAutocomplete("mtypes_search_val", "mtypes_autocomplete_box", "mtypes_search_att", "/api/suggest_mtypes");
    }
});
