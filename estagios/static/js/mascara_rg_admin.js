document.addEventListener('DOMContentLoaded', function() {
    // O Django Admin sempre dá o ID "id_nomedocampo" para os inputs
    var rgInput = document.getElementById('id_rg');

    if (rgInput) {
        rgInput.addEventListener('input', function(e) {
            var value = e.target.value;
            var input = e.target;

            // Remove tudo que não é dígito
            value = value.replace(/\D/g, "");

            // Trava em 12 dígitos
            if (value.length > 12) value = value.slice(0, 12);

            // Aplica a máscara
            value = value.replace(/(\d{2})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");

            e.target.value = value;
        });
    }
});