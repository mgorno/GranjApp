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

  // Cuando cambias el producto seleccionado, carga unidad y precio
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

    // Clona la fila plantilla
    const fila = tpl.cloneNode(true);

    // Setea los valores en inputs ocultos y textos visibles
    fila.querySelector('input[name="id_producto"]').value = opt.value;
    fila.querySelector('.nombre').textContent = opt.dataset.desc;

    fila.querySelector('span.cantidad').textContent = c;
    fila.querySelector('input[name="cantidad"]').value = c;

    fila.querySelector('input[name="unidad"]').value = unidad.textContent;
    fila.querySelector('.unidad-base').textContent = unidad.textContent;

    fila.querySelector('span.precio').textContent = p.toFixed(2);
    fila.querySelector('input[name="precio"]').value = p.toFixed(2);

    // Agrega la fila a la tabla
    tabla.appendChild(fila);

    // Limpia inputs para la próxima carga
    sel.selectedIndex = 0;
    cant.value = '';
    unidad.textContent = '';
    precio.value = '';

    // Recalcula total
    let suma = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      suma += parseFloat(tr.querySelector('input[name="precio"]').value) *
              parseFloat(tr.querySelector('input[name="cantidad"]').value);
    });
    total.textContent = suma.toFixed(2);
  });

  // Evento para eliminar fila
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();

      // Recalcula total al eliminar
      let suma = 0;
      tabla.querySelectorAll('tr').forEach(tr => {
        suma += parseFloat(tr.querySelector('input[name="precio"]').value) *
                parseFloat(tr.querySelector('input[name="cantidad"]').value);
      });
      total.textContent = suma.toFixed(2);
    }
  });
});
