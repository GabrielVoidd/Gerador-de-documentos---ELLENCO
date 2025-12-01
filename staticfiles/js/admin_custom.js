window.addEventListener("load", function() {
    (function($) {
        $('#result_list tbody tr').each(function() {
            // Verifica se a célula com a classe .field-restrito tem o ícone de 'icon-no'
            // IMPORTANTE: Verifique se o nome da classe é 'field-restrito' inspecionando o elemento
            if ($(this).find('.field-restrito img[src*="icon-no"]').length > 0) {
                $(this).css('background-color', '#ffe6e6'); // Pinta o fundo
                $(this).find('td, th').css('color', '#a80000');
            }
        });
    })(django.jQuery);
});