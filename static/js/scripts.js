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
      const input = btn.previousElementSibling;
      if (input.hasAttribute('readonly')) {
        input.removeAttribute('readonly');
        input.focus();
        btn.classList.remove('btn-outline-light');
        btn.classList.add('btn-warning');
      } else {
        input.setAttribute('readonly', true);
        btn.classList.add('btn-outline-light');
        btn.classList.remove('btn-warning');
      }
    });
  });
});