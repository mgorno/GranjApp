document.addEventListener('DOMContentLoaded', () => {
  const sel     = document.getElementById('selProducto');
  const cantInp = document.getElementById('inpCantidad');
  const unidad  = document.getElementById('inpUnidad');
  const precio  = document.getElementById('inpPrecio');
  const tabla   = document.querySelector('#tabla-detalle tbody');
  const tpl     = document.getElementById('fila-template').content;
  const addBtn  = document.getElementById('btnAddLinea');
  const total   = document.getElementById('totalGeneral');

  if (!sel || !cantInp || !unidad || !precio || !tabla || !tpl || !addBtn || !total) {
    console.error('Faltan elementos para pedidoDetalle.js');
    return;
  }

  /* Al seleccionar producto → unidad y precio */
  sel.addEventListener('change', () => {
    const opt = sel.selectedOptions[0];
    if (!opt) return;
    unidad.textContent = opt.dataset.unidad || '';
    precio.value       = opt.dataset.precio || '';
  });

  /* Añadir línea */
  addBtn.addEventListener('click', () => {
    const opt = sel.selectedOptions[0];
    const cantidad = Number(cantInp.value);
    const precioNum = Number(precio.value);

    if (!opt || !opt.value)            return alert('Elegí un producto.');
    if (cantidad < 1)                  return alert('Cantidad inválida.');
    if (!precioNum || precioNum <= 0)  return alert('Precio inválido.');

    /* Evitar duplicados */
    if ([...tabla.querySelectorAll('input[name="id_producto"]')]
          .some(i => i.value === opt.value)) {
      return alert('Ese producto ya está en el detalle.');
    }

    /* Clonar fila y completar */
    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value = opt.value;
    fila.querySelector('.nombre').textContent             = opt.dataset.desc;

    fila.querySelector('input[name="cantidad"]').value    = cantidad;
    fila.querySelector('.cantidad').textContent           = cantidad;

    fila.querySelector('input[name="unidad"]').value      = unidad.textContent;
    fila.querySelector('.unidad-base').textContent        = unidad.textContent;

    fila.querySelector('input[name="precio"]').value      = precioNum.toFixed(2);
    fila.querySelector('.precio').textContent             = precioNum.toFixed(2);

    tabla.appendChild(fila);

    /* Limpiar inputs */
    sel.selectedIndex = 0;
    cantInp.value = '';
    unidad.textContent = '';
    precio.value = '';

    recalcularTotal();
  });

  /* Eliminar línea */
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      recalcularTotal();
    }
  });

  function recalcularTotal() {
    let sum = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      sum += parseFloat(tr.querySelector('input[name="precio"]').value) *
             parseFloat(tr.querySelector('input[name="cantidad"]').value);
    });
    total.textContent = sum.toFixed(2);
  }
});
