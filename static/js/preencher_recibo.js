// Use 'django.jQuery' em vez de '$'
(function($) {
    $(document).ready(function() {
        // 1. Encontre o <select> do contrato
        // O Django admin usualmente cria o ID como 'id_nome_do_campo'
        var contratoSelect = $('#id_contrato');

        function preencherDadosContrato() {
            var contratoId = contratoSelect.val(); // Pega o ID do contrato selecionado

            if (contratoId) {
                fetch(`/api/get-contrato-data/${contratoId}/`)
                    .then(response => response.json())
                    .then(data => {
                        // 4. Preencha os campos do formulário
                        // Use os IDs corretos dos seus campos
                        $('#id_estagiario_nome').val(data.estagiario_nome);
                        $('#id_parte_concedente_nome').val(data.parte_concedente_nome);
                        $('#id_valor_bolsa').val(data.valor_bolsa);
                        $('#id_data_inicio').val(data.data_inicio);
                        $('#id_data_fim').val(data.data_fim);
                    })
                    .catch(error => console.error('Erro ao buscar dados do contrato:', error));
            }
        }

        // 5. Monitore mudanças no <select> do contrato
        contratoSelect.on('change', preencherDadosContrato);

        if ($('#id_estagiario_nome').val() == '') {
             preencherDadosContrato();
        }
    });
})(django.jQuery);