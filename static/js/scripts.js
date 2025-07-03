document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('buscarCliente');
  
  input.addEventListener('input', () => {
    const filtro = input.value.toLowerCase();
    const clientes = document.querySelectorAll('.cliente-item');

    clientes.forEach(cliente => {
      const nombre = cliente.querySelector('div').textContent.toLowerCase();
      const collapseId = cliente.querySelector('a').getAttribute('href');
      const detalle = document.querySelector(collapseId);

      if (nombre.includes(filtro)) {
        cliente.style.display = '';
        if (detalle) detalle.style.display = '';
      } else {
        cliente.style.display = 'none';
        if (detalle) detalle.style.display = 'none';
      }
    });
  });
});


document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn-editar-campo').forEach(btn => {
    btn.addEventListener('click', () => {
      const row   = btn.closest('.d-flex');
      const span  = row.querySelector('.valor-campo');
      const input = row.querySelector('input');

      // Cambiar a modo edición
      if (span && !span.classList.contains('d-none')) {
        span.classList.add('d-none');
        input.classList.remove('d-none');
        input.focus();
        btn.classList.remove('btn-outline-light');
        btn.classList.add('btn-warning');
      }
      // Volver a modo solo lectura (si vuelven a tocar el lápiz)
      else {
        span.textContent = input.value || span.textContent;
        span.classList.remove('d-none');
        input.classList.add('d-none');
        btn.classList.add('btn-outline-light');
        btn.classList.remove('btn-warning');
      }
    });
  });
});
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn-editar-campo').forEach(btn => {
    btn.addEventListener('click', () => {
      const row   = btn.closest('.d-flex');
      const span  = row.querySelector('.valor-campo');
      const input = row.querySelector('input');

      // Cambiar a modo edición
      if (span && !span.classList.contains('d-none')) {
        span.classList.add('d-none');
        input.classList.remove('d-none');
        input.focus();
        btn.classList.remove('btn-outline-light');
        btn.classList.add('btn-warning');
      }
      // Volver a modo solo lectura (si vuelven a tocar el lápiz)
      else {
        span.textContent = input.value || span.textContent;
        span.classList.remove('d-none');
        input.classList.add('d-none');
        btn.classList.add('btn-outline-light');
        btn.classList.remove('btn-warning');
      }
    });
  });
});
