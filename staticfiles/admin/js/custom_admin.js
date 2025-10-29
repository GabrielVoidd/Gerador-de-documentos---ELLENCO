// Forma segura de carregar o jQuery do Django
(function($) {
    $(document).ready(function() {
        // 1. Encontrar o índice da coluna 'restrito' no cabeçalho (th)
        let restritoIndex = -1;
        $('#result_list thead th').each(function(index) {
            // O Django adiciona uma classe 'column-<nome_do_campo>'
            if ($(this).hasClass('column-restrito')) {
                restritoIndex = index;
                return false; // Sai do loop
            }
        });

        // Se não encontrou a coluna, não faz nada
        if (restritoIndex === -1) {
            return;
        }

        // 2. Iterar por cada linha (tr) da tabela
        $('#result_list tbody tr').each(function() {
            let row = $(this);

            // 3. Achar a célula (td) correta na linha
            let cell = row.children().eq(restritoIndex);

            // 4. Verificar se o valor é "True"
            // O admin do Django renderiza BooleanField=True com um ícone
            // que tem o alt="True" (ou "Sim", dependendo da tradução)
            if (cell.find('img[alt="True"]').length > 0 || cell.find('img[alt="Sim"]').length > 0) {

                // 5. Adicionar nossa classe CSS na linha (tr) inteira!
                row.addClass('linha-restrita');
            }
        });
    });
})(django.jQuery);