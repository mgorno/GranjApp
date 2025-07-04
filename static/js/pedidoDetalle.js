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

  sel.addEventListener('change', () => {
    const opt = sel.selectedOptions[0];
    unidad.textContent = opt.dataset.unidad || '';
    precio.value = opt.dataset.precio || '';
  });

  btn.addEventListener('click', () => {
    const opt = sel.selectedOptions[0];
    const c = Number(cant.value);
    const p = Number(precio.value);

    if (!opt || !opt.value || c < 1 || p <= 0) {
      alert('Completar todos los campos correctamente.');
      return;
    }

    const fila = tpl.cloneNode(true);

    fila.querySelector('input[name="id_producto"]').value = opt.value;
    fila.querySelector('.nombre').textContent = opt.dataset.desc;

    fila.querySelector('input[name="cantidad"]').value = c;
    fila.querySelector('.cantidad').textContent = c;

    fila.querySelector('input[name="unidad"]').value = unidad.textContent;
    fila.querySelector('.unidad-base').textContent = unidad.textContent;

    fila.querySelector('input[name="precio"]').value = p.toFixed(2);
    fila.querySelector('.precio').textContent = p.toFixed(2);

    tabla.appendChild(fila);

    // Limpiar inputs para el próximo producto
    sel.selectedIndex = 0;
    cant.value = '';
    unidad.textContent = '';
    precio.value = '';

    // Recalcular total
    actualizarTotal();
  });

  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      actualizarTotal();
    }
  });

  function actualizarTotal() {
    let suma = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      const precio = parseFloat(tr.querySelector('input[name="precio"]').value) || 0;
      const cantidad = parseFloat(tr.querySelector('input[name="cantidad"]').value) || 0;
      suma += precio * cantidad;
    });
    total.textContent = suma.toFixed(2);
  }
});
