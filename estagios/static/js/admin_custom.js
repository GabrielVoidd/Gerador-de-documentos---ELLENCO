window.addEventListener("load", function() {
    (function($) {
        console.log("Versão com 3 cores carregadas");
        // Itera sobre cada linha da tabela de resultados
        $('#result_list tbody tr').each(function() {
            var $row = $(this); // Cache do seletor

            // --- 1. Restrito (Indica atenção ou limitação - Laranja) ---
            // Verifica se tem o ícone de 'yes' na coluna de restrito
            if ($row.find('.field-restrito img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#f39c12');
                $row.find('td, th').css('color', '#ffffff');
            }

            // --- 2. Stand by (Indica pausa / espera - Amarelo) ---
            else if ($row.find('.field-stand_by img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#f7f55c');
                $row.find('td, th').css('color', '#000000');
            }

            // --- 3. TRABALHANDO (Indica andamento / positividade - Verde) ---
            else if ($row.find('.field-trabalhando img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#bdffc7');
                $row.find('td, th').css('color', '#2ad444');
            }

            // --- 4. Aprovado (Indica sucesso / conclusão - Verde escuro) ---
            else if ($row.find('.field-aprovado img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#27ae60');
                $row.find('td, th').css('color', '#ffffff');
            }

            // --- 5. Reprovado (Indica erro / falha - Vermelho) ---
            else if ($row.find('.field-reprovado img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#e74c3c');
                $row.find('td, th').css('color', '#ffffff');
            }

            // --- 6. Não Compareceu (Indice ausência / neutralidade - Cinza Claro) ---
            else if ($row.find('.field-nao_compareceu img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#bdc3c7');
                $row.find('td, th').css('color', '#ffffff');
            }

            // --- 7. Desistiu (Indica desistência - Cinza Médio) ---
            else if ($row.find('.field-desistiu img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#7f8c8d');
                $row.find('td, th').css('color', '#ffffff');
            }

            // --- 8. Encaminhado (Indica transferência - Azul) ---
            else if ($row.find('.field-encaminhado img[src*="icon-yes"]').length > 0) {
                $row.css('background-color', '#3498db');
                $row.find('td, th').css('color', '#ffffff');
            }
        });
    })(django.jQuery);
});