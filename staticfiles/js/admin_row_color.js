document.addEventListener('DOMContentLoaded', function() {
    // Procura por todos os spans indicadores
    const indicators = document.querySelectorAll('.row-color-indicator');

    indicators.forEach(function(indicator) {
        const color = indicator.dataset.color;

        // Se houver uma cor definida
        if (color) {
            // Encontra a linha (TR) pai desse indicador
            const row = indicator.closest('tr');
            if (row) {
                // Aplica a cor de fundo na linha inteira
                row.style.backgroundColor = color;

                // Opcional: Se a cor for muito escura (vermelho forte),
                // talvez queira deixar o texto branco ou negrito para ler melhor
                if (color === "#ff6666") {
                    row.style.fontWeight = "bold";
                    // row.style.color = "white"; // Descomente se precisar de mais contraste
                }
            }
        }
    });
});