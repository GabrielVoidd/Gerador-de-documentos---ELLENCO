window.addEventListener("load", function() {
    (function($) {
        // Itera sobre cada linha da tabela de resultados
        $('#result_list tbody tr').each(function() {
            var $row = $(this); // Cache do seletor

            // --- 1. RESTRITO (Prioridade Alta - Vermelho) ---
            // Verifica se tem o ícone de 'yes' na coluna de restrito
            if ($row.find('.field-restrito img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#ffe6e6');
                $row.find('td, th').css('color', '#a80000');
            }

            // --- 2. STAND BY (Roxo) ---
            // IMPORTANTE: Ajuste o seletor '.field-status' e o texto 'Stand by' conforme seu HTML real
            else if ($row.find('.field-stand_by img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#f9b8ff');
                $row.find('td, th').css('color', '#b332bf');
            }

            // --- 3. TRABALHANDO (Verde) ---
            // IMPORTANTE: Ajuste o seletor '.field-status' e o texto 'Trabalhando'
            else if ($row.find('.field-trabalhando img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#bdffc7');
                $row.find('td, th').css('color', '#2ad444');
            }
        });
    })(django.jQuery);
});