(function($) {
    $(document).ready(function() {
        var contratoSelect = $('#id_contrato');

        function preencherDadosContrato() {
            var contratoId = contratoSelect.val();

            if (contratoId) {
                // URL absoluta para evitar problemas de rota
                var url = `/api/get-contrato-data/${contratoId}/`;

                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Erro na resposta da API');
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Preencha os campos apenas se eles existirem
                        if ($('#id_estagiario_nome').length) $('#id_estagiario_nome').val(data.estagiario_nome || '');
                        if ($('#id_parte_concedente_nome').length) $('#id_parte_concedente_nome').val(data.parte_concedente_nome || '');
                        if ($('#id_valor_bolsa').length) $('#id_valor_bolsa').val(data.valor_bolsa || '');
                        if ($('#id_data_inicio').length) $('#id_data_inicio').val(data.data_inicio || '');
                        if ($('#id_data_fim').length) $('#id_data_fim').val(data.data_fim || '');
                    })
                    .catch(error => console.error('Erro ao buscar dados do contrato:', error));
            }
        }

        contratoSelect.on('change', preencherDadosContrato);

        // Preenche automaticamente se o campo estagiario_nome estiver vazio
        if ($('#id_estagiario_nome').length && $('#id_estagiario_nome').val() === '') {
            preencherDadosContrato();
        }
    });
})(django.jQuery || jQuery); // Fallback para jQuery global se necessário