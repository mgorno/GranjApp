// === Exportar a Excel ===
document.getElementById("btn-exportar-excel").addEventListener("click", function () {
    const form = document.getElementById("form-exportar");
    const url = new URL(form.action, window.location.origin);
    const params = new URLSearchParams(new FormData(form));
    url.search = params;

    const link = document.createElement("a");
    link.href = url.toString();
    link.download = "movimientos_cuenta_corriente.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Redirigir después de 2 segundos (opcional)
    setTimeout(() => {
        window.location.href = "/cuenta_corriente"; // Usar ruta directa sin Jinja
    }, 2000);
});

// === Formateo en tiempo real para inputs de monto ===

// Función que formatea un número como "$1.234.567"
function formatoPrecioArg(valor) {
    let numero = valor.replace(/\D/g, ''); // Elimina todo lo que no sea dígito
    if (!numero) return '';
    return numero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// Función auxiliar para limpiar puntos y signo $
function limpiarPrecioFormateado(valor) {
    return valor.replace(/\./g, '').replace('$', '');
}

// Al cargar la página, aplicar el formateo en todos los inputs con clase .formatear-precio
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.formatear-precio').forEach(input => {
        input.addEventListener('input', function () {
            const cursorPos = this.selectionStart;

            const rawValue = this.value.replace(/\./g, '').replace('$', '');
            this.value = formatoPrecioArg(rawValue);

            this.setSelectionRange(cursorPos, cursorPos);
        });
    });
});
