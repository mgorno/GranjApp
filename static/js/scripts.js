document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('buscarCliente');

    input.addEventListener('input', () => {
        const filtro = input.value.toLowerCase();
        const clientes = document.querySelectorAll('.cliente-item');

        clientes.forEach(cliente => {
            const nombre = cliente.querySelector('.nombre-cliente').textContent.toLowerCase();
            const idCollapse = cliente.querySelector('a').getAttribute('href');
            const detalle = document.querySelector(idCollapse);

            const coincide = nombre.includes(filtro);

            cliente.style.display = coincide ? '' : 'none';
            if (detalle) detalle.style.display = coincide ? '' : 'none';
        });
    });
});



document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-editar-campo').forEach(btn => {
        btn.addEventListener('click', () => {
            const wrapper = btn.closest('.d-flex');
            const input = wrapper.querySelector('input');
            const span = wrapper.querySelector('.valor-campo');

            // Alternar visibilidad
            input.classList.toggle('d-none');
            span.classList.toggle('d-none');

            // Poner foco en el input si se está editando
            if (!input.classList.contains('d-none')) {
                input.focus();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
  const tbody   = document.querySelector('#tabla-detalle tbody');
  const tpl     = document.getElementById('fila-template').content;
  const formNew = document.getElementById('formNuevoItem');
  const offcanvas = bootstrap.Offcanvas.getOrCreateInstance('#offNuevoItem');

  /* Añadir producto desde off‑canvas */
  formNew.addEventListener('submit', e => {
    e.preventDefault();
    const sel = document.getElementById('selProducto');
    const cant= document.getElementById('inpCantidad').value;
    const prec= document.getElementById('inpPrecio').value || sel.selectedOptions[0].dataset.precio;

    if (!sel.value) return;

    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value = sel.value;
    fila.querySelector('.nombre').textContent = sel.selectedOptions[0].dataset.desc;
    fila.querySelector('input[name="cantidad"]').value = cant || 1;
    fila.querySelector('input[name="precio"]').value   = prec || '';

    tbody.appendChild(fila);
    formNew.reset();
    offcanvas.hide();
  });

  /* Eliminar fila */
  tbody.addEventListener('click', e => {
    if (e.target.closest('.eliminar')) e.target.closest('tr').remove();
  });

  /* Filtro en vivo (opcional) */
  const busc = document.getElementById('buscarFila');
  if (busc) busc.addEventListener('input', () => {
    const f = busc.value.toLowerCase().trim();
    tbody.querySelectorAll('tr').forEach(row => {
      const txt = row.querySelector('.nombre').textContent.toLowerCase();
      row.style.display = txt.includes(f) ? '' : 'none';
    });
  });
});