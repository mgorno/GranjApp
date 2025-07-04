document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('selProducto');
  const cant = document.getElementById('inpCantidad');
  const unidad = document.getElementById('inpUnidad');
  const precio = document.getElementById('inpPrecio');
  const tabla = document.querySelector('#tabla-detalle tbody');
  const tpl = document.getElementById('fila-template').content;
  const btn = document.getElementById('btnAddLinea');
  const total = document.getElementById('totalGeneral');

  if (!sel || !cant || !unidad || !precio || !tabla || !tpl || !btn || !total) return;

  // Cuando cambias de producto, carga unidad y precio
  sel.addEventListener('change', () => {
    const opt = sel.selectedOptions[0];
    unidad.textContent = opt.dataset.unidad || '';
    precio.value = opt.dataset.precio || '';
  });

  btn.addEventListener('click', () => {
    const opt = sel.selectedOptions[0];
    const c = Number(cant.value);
    const p = Number(precio.value);

    if (!opt || !opt.value) return alert('Elegí un producto válido.');
    if (c < 1) return alert('Ingresá una cantidad válida.');
    if (p <= 0 || isNaN(p)) return alert('Precio inválido.');

    // Verificar si el producto ya está agregado
    const yaAgregado = Array.from(tabla.querySelectorAll('input[name="id_producto"]'))
      .some(input => input.value === opt.value);
    if (yaAgregado) {
      alert('El producto ya está agregado al detalle.');
      return;
    }

    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value = opt.value;
    fila.querySelector('.nombre').textContent = opt.dataset.desc;
    const cantidadInput = fila.querySelector('input[name="cantidad"]');
    cantidadInput.value = c;
    cantidadInput.readOnly = true;
    fila.querySelector('input[name="unidad"]').value = unidad.textContent;
    fila.querySelector('.unidad-base').textContent = unidad.textContent;
    const precioInput = fila.querySelector('input[name="precio"]');
    precioInput.value = p.toFixed(2);
    precioInput.readOnly = true;

    tabla.appendChild(fila);

    // Limpiar inputs y select
    sel.selectedIndex = 0;
    unidad.textContent = '';
    precio.value = '';
    cant.value = '';

    // Recalcular total
    actualizarTotal();
  });

  // Función para actualizar total
  function actualizarTotal() {
    let sum = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      const precio = parseFloat(tr.querySelector('input[name="precio"]').value) || 0;
      const cantidad = parseFloat(tr.querySelector('input[name="cantidad"]').value) || 0;
      sum += precio * cantidad;
    });
    total.textContent = sum.toFixed(2);
  }

  // Eliminar fila y actualizar total
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      actualizarTotal();
    }
  });
});
