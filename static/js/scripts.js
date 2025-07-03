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
