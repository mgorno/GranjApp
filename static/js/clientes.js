document.addEventListener('DOMContentLoaded', () => {
  // Buscador
  const input = document.getElementById('buscarCliente');
  if (input) {
    input.addEventListener('input', () => {
      const filtro = input.value.toLowerCase();
      const clientes = document.querySelectorAll('.list-group > .list-group-item');

      clientes.forEach(cliente => {
        const nombre = cliente.querySelector('.flex-grow-1 strong').textContent.toLowerCase();
        const detalle = cliente.nextElementSibling;
        const coincide = nombre.includes(filtro);

        cliente.style.display = coincide ? '' : 'none';
        if (detalle) detalle.style.display = coincide ? '' : 'none';
      });
    });
  }

  // Botón editar por campo
  document.querySelectorAll('.btn-editar-campo').forEach(btn => {
    btn.addEventListener('click', () => {
      const parent = btn.closest('.d-flex.align-items-center.gap-2');
      if (!parent) return;

      const span = parent.querySelector('.valor-campo');
      const input = parent.querySelector('input');

      if (span && input) {
        span.classList.add('d-none');
        input.classList.remove('d-none');
        input.focus();
        btn.classList.add('d-none');
      }
    });
  });

  // Cuando se cierra el accordion (collapse), vuelve todo a modo solo lectura
  document.querySelectorAll('.accordion-collapse').forEach(collapse => {
    collapse.addEventListener('hidden.bs.collapse', () => {
      const inputs = collapse.querySelectorAll('input:not(.d-none)');
      inputs.forEach(input => {
        const parent = input.closest('.d-flex.align-items-center.gap-2');
        if (!parent) return;
        const span = parent.querySelector('.valor-campo');
        const btn = parent.querySelector('.btn-editar-campo');

        if (span && btn) {
          input.classList.add('d-none');
          span.classList.remove('d-none');
          btn.classList.remove('d-none');
        }
      });
    });
  });
});
