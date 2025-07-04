document.addEventListener('DOMContentLoaded', () => {
  const selProducto = document.getElementById('selProducto');
  const inpCantidad = document.getElementById('inpCantidad');
  const inpUnidad   = document.getElementById('inpUnidad');
  const inpPrecio   = document.getElementById('inpPrecio');
  const tabla       = document.querySelector('#tabla-detalle tbody');
  const tpl         = document.getElementById('fila-template').content;
  const btnAdd      = document.getElementById('btnAddLinea');
  const total       = document.getElementById('totalGeneral');

  if (!selProducto || !inpCantidad || !inpUnidad || !inpPrecio || !tabla || !tpl || !btnAdd || !total) return;

  // Cuando cambia el producto, actualizar unidad y precio
  selProducto.addEventListener('change', () => {
    const opt = selProducto.selectedOptions[0];
    inpUnidad.textContent = opt.dataset.unidad || '';
    inpPrecio.value = parseFloat(opt.dataset.precio || 0).toFixed(2);
  });

  // Añadir línea al detalle
  btnAdd.addEventListener('click', () => {
    const opt = selProducto.selectedOptions[0];
    const idProd = opt?.value;
    const desc   = opt?.dataset?.desc;
    const unidad = opt?.dataset?.unidad;
    const precio = parseFloat(inpPrecio.value);
    const cant   = parseFloat(inpCantidad.value);

    if (!idProd || cant <= 0 || precio <= 0) {
      alert("Completar los campos correctamente.");
      return;
    }

    // Validar que no esté ya agregado
    const yaExiste = [...tabla.querySelectorAll('input[name="id_producto"]')]
                      .some(input => input.value === idProd);
    if (yaExiste) {
      alert("Ese producto ya está en el detalle.");
      return;
    }

    // Clonar la fila y cargar datos
    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value = idProd;
    fila.querySelector('.nombre').textContent = desc;
    fila.querySelector('input[name="cantidad"]').value = cant;
    fila.querySelector('input[name="unidad"]').value = unidad;
    fila.querySelector('.unidad-base').textContent = unidad;
    fila.querySelector('input[name="precio"]').value = precio.toFixed(2);
    fila.querySelector('input[name="cantidad"]').readOnly = true;
    fila.querySelector('input[name="precio"]').readOnly = true;

    tabla.appendChild(fila);

    // Desactivar required para evitar bloqueo en el submit
    selProducto.required = inpCantidad.required = inpPrecio.required = false;

    // Limpiar inputs
    selProducto.selectedIndex = 0;
    inpCantidad.value = '';
    inpUnidad.textContent = '';
    inpPrecio.value = '';

    // Recalcular total
    let sum = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      const c = parseFloat(tr.querySelector('input[name="cantidad"]').value);
      const p = parseFloat(tr.querySelector('input[name="precio"]').value);
      sum += c * p;
    });
    total.textContent = sum.toFixed(2);
  });

  // Eliminar línea
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      // Recalcular total
      let sum = 0;
      tabla.querySelectorAll('tr').forEach(tr => {
        const c = parseFloat(tr.querySelector('input[name="cantidad"]').value);
        const p = parseFloat(tr.querySelector('input[name="precio"]').value);
        sum += c * p;
      });
      total.textContent = sum.toFixed(2);
    }
  });
});
