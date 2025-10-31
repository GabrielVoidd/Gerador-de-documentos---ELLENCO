(function($) {
    $(document).ready(function() {
        function colorirLinhasRestritas() {
            let restritoIndex = -1;

            // Procura a coluna 'restrito' no cabeçalho
            $('#result_list thead th').each(function(index) {
                if ($(this).hasClass('column-restrito') ||
                    $(this).text().trim().toLowerCase().includes('restrito')) {
                    restritoIndex = index;
                    return false;
                }
            });

            if (restritoIndex === -1) {
                console.log('Coluna "restrito" não encontrada');
                return;
            }

            console.log('Índice da coluna restrito:', restritoIndex);

            // Itera pelas linhas
            $('#result_list tbody tr').each(function() {
                let row = $(this);
                let cells = row.find('td');
                let cell = cells.eq(restritoIndex);

                console.log('Conteúdo da célula restrito:', cell.html());

                // Múltiplas formas de verificar se é True
                let isRestrito = false;

                // 1. Verifica ícones do Django Admin
                if (cell.find('img[alt="True"]').length > 0 ||
                    cell.find('img[alt="Sim"]').length > 0) {
                    isRestrito = true;
                }
                // 2. Verifica por texto
                else if (cell.text().trim().toLowerCase() === 'true' ||
                         cell.text().trim().toLowerCase() === 'sim' ||
                         cell.text().trim().toLowerCase() === 'verdadeiro') {
                    isRestrito = true;
                }
                // 3. Verifica por classes específicas (ícone de check)
                else if (cell.find('.icon-yes').length > 0 ||
                         cell.find('.icon-check').length > 0) {
                    isRestrito = true;
                }
                // 4. Verifica se há elementos visíveis (não vazios)
                else if (cell.children().length > 0 &&
                         cell.text().trim() !== '' &&
                         cell.text().trim() !== '@') {
                    isRestrito = true;
                }

                if (isRestrito) {
                    row.addClass('linha-restrita');
                    console.log('Linha marcada como restrita');
                }
            });
        }

        // Executa e observa mudanças
        colorirLinhasRestritas();

        // Para debugging - ver todas as colunas
        console.log('Cabeçalhos da tabela:');
        $('#result_list thead th').each(function(index) {
            console.log(`Coluna ${index}:`, $(this).attr('class'), '-', $(this).text().trim());
        });
    });
})(django.jQuery);