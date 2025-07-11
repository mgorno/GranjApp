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
        window.location.href = "{{ url_for('cuenta_corriente.cuenta_corriente') }}";
    }, 2000);
});
