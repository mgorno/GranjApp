document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-pagos');
  const btn = document.getElementById('btnGuardarPago');

  form.addEventListener('submit', () => {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
  });
});
