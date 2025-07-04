document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('buscarCliente');
  if (!input) return;

  input.addEventListener('input', () => {
    const filtro   = input.value.toLowerCase();
    const clientes = document.querySelectorAll('.cliente-item');

    clientes.forEach(cliente => {
      const nombre     = cliente.querySelector('.nombre-cliente').textContent.toLowerCase();
      const idCollapse = cliente.querySelector('a').getAttribute('href');
      const detalle    = document.querySelector(idCollapse);
      const coincide   = nombre.includes(filtro);

      cliente.style.display = coincide ? '' : 'none';
      if (detalle) detalle.style.display = coincide ? '' : 'none';
    });
  });
});
