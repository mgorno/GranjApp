// ==== Formato de monto con puntos de miles y símbolo $ ====

function formatoPrecioArg(valor) {
  let numero = valor.replace(/\D/g, ''); // Elimina todo lo que no sea dígito
  if (!numero) return '';
  return numero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

function limpiarPrecioFormateado(valor) {
  return valor.replace(/\./g, '').replace('$', '');
}

// ==== Cuando el DOM carga ====

document.addEventListener('DOMContentLoaded', () => {

  // 1. Deshabilitar botón al enviar formulario de pagos
  const form = document.getElementById('form-pagos');
  const btn = document.getElementById('btnGuardarPago');

  if (form && btn) {
    form.addEventListener('submit', () => {
      btn.disabled = true;
      btn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Procesando...`;
    });
  }

  // 2. Aplicar formato de precio en tiempo real
  document.querySelectorAll('.formatear-precio').forEach(input => {
    input.addEventListener('input', function () {
      const cursorPos = this.selectionStart;

      const rawValue = this.value.replace(/\./g, '').replace('$', '');
      this.value = formatoPrecioArg(rawValue);

      this.setSelectionRange(cursorPos, cursorPos);
    });
  });

});
