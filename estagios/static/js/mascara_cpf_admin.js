document.addEventListener('DOMContentLoaded', function() {
    // O Django Admin sempre dá o ID "id_nomedocampo" para os inputs
    var cpfInput = document.getElementById('id_cpf');

    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            var value = e.target.value;
            var input = e.target;

            // Remove tudo que não é dígito
            value = value.replace(/\D/g, "");

            // Trava em 11 dígitos
            if (value.length > 11) value = value.slice(0, 11);

            // Aplica a máscara
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

            e.target.value = value;
        });
    }
});