document.addEventListener('DOMContentLoaded', () => {
  const sel   = document.getElementById('selProducto');
  const cInp  = document.getElementById('inpCantidad');
  const uSpan = document.getElementById('inpUnidad');
  const pInp  = document.getElementById('inpPrecio');
  const tabla = document.querySelector('#tabla-detalle tbody');
  const tpl   = document.getElementById('fila-template').content;
  const addBt = document.getElementById('btnAddLinea');
  const tot   = document.getElementById('totalGeneral');

  if (!sel || !cInp || !uSpan || !pInp || !tabla || !tpl || !addBt || !tot) return;

  /* Cargar unidad y precio al cambiar producto */
  sel.addEventListener('change', () => {
    const o = sel.selectedOptions[0];
    uSpan.textContent = o.dataset.unidad || '';
    pInp.value        = o.dataset.precio || '';
  });

  /* Añadir producto */
  addBt.addEventListener('click', () => {
    const o       = sel.selectedOptions[0];
    const idProd  = o?.value;
    const desc    = o?.dataset?.desc;
    const unidad  = o?.dataset?.unidad;
    const precio  = parseFloat(pInp.value);
    const cant    = parseFloat(cInp.value);

    if (!idProd)        return alert('Elegí un producto.');
    if (!cant || cant<=0)   return alert('Cantidad inválida.');
    if (!precio || precio<=0) return alert('Precio inválido.');

    /* Evitar duplicados */
    if ([...tabla.querySelectorAll('input[name="id_producto"]')]
        .some(input => input.value === idProd)) {
      alert('Ese producto ya está en el detalle.');
      return;
    }

    const fila = tpl.cloneNode(true);

    fila.querySelector('input[name="id_producto"]').value = idProd;
    fila.querySelector('.nombre').textContent             = desc;

    fila.querySelector('input[name="cantidad"]').value    = cant;
    fila.querySelector('.cantidad').textContent           = cant;

    fila.querySelector('input[name="unidad"]').value      = unidad;
    fila.querySelector('.unidad-base').textContent        = unidad;

    fila.querySelector('input[name="precio"]').value      = precio.toFixed(2);
    fila.querySelector('.precio').textContent             = precio.toFixed(2);

    tabla.appendChild(fila);

    /* Desactivar required para evitar bloqueo al enviar */
    sel.required = cInp.required = pInp.required = false;

    /* Limpiar para siguiente carga */
    sel.selectedIndex = 0;
    cInp.value = '';
    uSpan.textContent = '';
    pInp.value = '';

    recalcularTotal();
  });

  /* Eliminar línea */
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      recalcularTotal();
      /* Si no queda ningún producto, volvemos a exigir required */
      if (tabla.querySelectorAll('tr').length === 0) {
        sel.required = cInp.required = pInp.required = true;
      }
    }
  });

  function recalcularTotal() {
    let suma = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      const c = parseFloat(tr.querySelector('input[name="cantidad"]').value) || 0;
      const p = parseFloat(tr.querySelector('input[name="precio"]').value)   || 0;
      suma += c * p;
    });
    tot.textContent = suma.toFixed(2);
  }
});
