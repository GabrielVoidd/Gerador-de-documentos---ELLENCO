// Usamos django.jQuery para evitar conflito com outras libs
(function($) {
    $(document).ready(function() {
        // Aplica a máscara no campo de data (o Django usa a classe vDateField)
        // Ou use o ID do seu campo: #id_data_nascimento
        $('.vDateField').mask('00/00/0000');

        // Dica extra: Máscara para CPF se precisar
        // $('#id_cpf').mask('000.000.000-00');
    });
})(django.jQuery);