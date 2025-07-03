document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('buscarCliente');
  input.addEventListener('input', () => {
    const filtro = input.value.toLowerCase();

    const clientes = document.querySelectorAll('.cliente-item');

    clientes.forEach(cliente => {
      const nombre = cliente.querySelector('div').textContent.toLowerCase();

      if (nombre.includes(filtro)) {
        cliente.style.display = '';
        const collapseId = cliente.querySelector('a').getAttribute('href');
        const detalle = document.querySelector(collapseId);
        if (detalle) detalle.style.display = '';
      } else {
        cliente.style.display = 'none';
        const collapseId = cliente.querySelector('a').getAttribute('href');
        const detalle = document.querySelector(collapseId);
        if (detalle) detalle.style.display = 'none';
      }
    });

    const letras = document.querySelectorAll('.letra-separador');
    letras.forEach(letra => {
      let next = letra.nextElementSibling;
      let hayVisible = false;
      while (next && !next.classList.contains('letra-separador')) {
        if (next.style.display !== 'none') {
          hayVisible = true;
          break;
        }
        next = next.nextElementSibling;
      }
      letra.style.display = hayVisible ? '' : 'none';
    });
  });
});
