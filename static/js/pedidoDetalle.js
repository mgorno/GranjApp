
  const tabla = document.querySelector('#tabla-detalle tbody');
  const tpl = document.getElementById('fila-template').content;
  const addBtn = document.getElementById('btnAddLinea');
  const selProducto = document.getElementById('selProducto');
  const cantidad = document.getElementById('inpCantidad');
  const unidad = document.getElementById('inpUnidad');
  const precio = document.getElementById('inpPrecio');
  const totalSpan = document.getElementById('total');

  selProducto.addEventListener('change', function () {
    const opt = this.selectedOptions[0];
    unidad.textContent = opt.dataset.unidadbase || '';
    if (!precio.value) precio.value = opt.dataset.precio || '';
  });

  addBtn.addEventListener('click', () => {
    if (!selProducto.value || !cantidad.value || cantidad.value < 1 || !precio.value || precio.value < 0) {
      alert('Completa todos los campos correctamente');
      return;
    }

    const fila = tpl.cloneNode(true);
    const tr = fila.querySelector('tr');

    const desc = selProducto.selectedOptions[0].dataset.desc;
    const unidadBase = selProducto.selectedOptions[0].dataset.unidadbase;

    tr.querySelector('input[name="id_producto"]').value = selProducto.value;
    tr.querySelector('.nombre').textContent = desc;
    tr.querySelector('input[name="cantidad"]').value = cantidad.value;
    tr.querySelector('input[name="unidad"]').value = unidadBase;
    tr.querySelector('.unidad-base').textContent = unidadBase;
    tr.querySelector('input[name="precio"]').value = precio.value;

    tabla.appendChild(fila);

    actualizarTotal();

    // Reset
    selProducto.value = '';
    cantidad.value = '';
    unidad.textContent = '';
    precio.value = '';
  });

  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      actualizarTotal();
    }
  });

  function actualizarTotal() {
    let total = 0;
    tabla.querySelectorAll('tr').forEach(tr => {
      const cant = parseFloat(tr.querySelector('input[name="cantidad"]').value);
      const prec = parseFloat(tr.querySelector('input[name="precio"]').value);
      total += cant * prec;
    });
    totalSpan.textContent = total.toFixed(2);
  }
