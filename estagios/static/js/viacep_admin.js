document.addEventListener('DOMContentLoaded', function() {
    // Pega o campo de CEP pelo ID padrão do Django Admin
    const cepInput = document.getElementById('id_cep');

    if (cepInput) {
        // Dispara a busca quando o usuário sair do campo de CEP (evento 'blur')
        cepInput.addEventListener('blur', function() {
            let cep = this.value.replace(/\D/g, ''); // Limpa caracteres não numéricos

            if (cep.length === 8) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(dados => {
                        if (!dados.erro) {
                            // Preenche os outros campos e passa para MAIÚSCULO
                            document.getElementById('id_bairro').value = dados.bairro.toUpperCase();
                            document.getElementById('id_endereco').value = dados.logradouro.toUpperCase();
                            document.getElementById('id_cidade').value = dados.localidade.toUpperCase();

                            // (Opcional) Trava o campo bairro para o usuário não mexer mais
                            document.getElementById('id_bairro').setAttribute('readonly', true);
                            document.getElementById('id_endereco').setAttribute('readonly', true);
                            document.getElementById('id_cidade').setAttribute('readonly', true);
                        } else {
                            alert("CEP não encontrado.");
                        }
                    })
                    .catch(error => console.error("Erro na consulta do CEP:", error));
            }
        });
    }
});