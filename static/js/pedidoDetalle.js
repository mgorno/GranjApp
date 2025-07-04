document.addEventListener('DOMContentLoaded', () => {
  const selProd   = document.getElementById('selProducto');
  const cantInput = document.getElementById('inpCantidad');
  const unidadLbl = document.getElementById('inpUnidad');
  const precioInp = document.getElementById('inpPrecio');
  const tabla     = document.querySelector('#tabla-detalle tbody');
  const tpl       = document.getElementById('fila-template').content;
  const addBtn    = document.getElementById('btnAddLinea');
  const totalLbl  = document.getElementById('totalGeneral');

  if (!selProd || !cantInput || !unidadLbl || !precioInp
      || !tabla || !tpl || !addBtn || !totalLbl) {
    console.error('Faltan elementos para pedidoDetalle.js');
    return;
  }

  selProd.addEventListener('change', () => {
    const opt = selProd.selectedOptions[0];
    unidadLbl.textContent = opt?.dataset.unidad || '';
    precioInp.value       = opt?.dataset.precio || '';
  });

  addBtn.addEventListener('click', () => {
    const opt  = selProd.selectedOptions[0];
    const cant = Number(cantInput.value);
    const prec = Number(precioInp.value);
    if (!opt?.value || cant < 1 || prec <= 0) {
      return alert('Completar producto, cantidad (>0) y precio (>0)');
    }

    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value  = opt.value;
    fila.querySelector('.nombre').textContent              = opt.dataset.desc;
    fila.querySelector('input[name="cantidad"]').value     = cant;
    fila.querySelector('input[name="unidad"]').value       = unidadLbl.textContent;
    fila.querySelector('.unidad-base').textContent         = unidadLbl.textContent;
    fila.querySelector('input[name="precio"]').value       = prec.toFixed(2);

    tabla.appendChild(fila);
    selProd.selectedIndex = 0;
    cantInput.value       = '';
    unidadLbl.textContent = '';
    precioInp.value       = '';
    actualizarTotal();
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
      const p = parseFloat(tr.querySelector('input[name="precio"]').value)   || 0;
      const c = parseFloat(tr.querySelector('input[name="cantidad"]').value) || 0;
      total += p * c;
    });
    totalLbl.textContent = total.toFixed(2);
  }
});
