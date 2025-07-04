document.addEventListener('DOMContentLoaded', () => {
  // --- Cliente/Fecha plegable ---
  const clienteForm = document.getElementById("cliente-fecha-form");
  const clienteSummary = document.getElementById("cliente-fecha-summary");
  const selectCliente = document.getElementById("selectCliente");
  const inputFecha = document.getElementById("inputFecha");
  const clienteNombreSpan = document.getElementById("cliente-nombre");
  const fechaEntregaSpan = document.getElementById("fecha-entrega");
  const btnEditar = document.getElementById("btnEditarClienteFecha");

  function actualizarResumen() {
    const clienteSeleccionado = selectCliente.options[selectCliente.selectedIndex];
    const clienteNombre = clienteSeleccionado ? clienteSeleccionado.text : "";
    const fecha = inputFecha.value;

    if (clienteNombre && fecha) {
      clienteNombreSpan.textContent = clienteNombre;
      fechaEntregaSpan.textContent = fecha;
      clienteForm.classList.add("d-none");
      clienteSummary.classList.remove("d-none");
    }
  }

  selectCliente.addEventListener("change", actualizarResumen);
  inputFecha.addEventListener("change", actualizarResumen);

  btnEditar.addEventListener("click", () => {
    clienteSummary.classList.add("d-none");
    clienteForm.classList.remove("d-none");
  });

  // --- Manejo productos ---
  const sel   = document.getElementById('selProducto');
  const cInp  = document.getElementById('inpCantidad');
  const uSpan = document.getElementById('inpUnidad');
  const pInp  = document.getElementById('inpPrecio');
  const tabla = document.querySelector('#tabla-detalle tbody');
  const tpl   = document.getElementById('fila-template').content;
  const addBt = document.getElementById('btnAddLinea');
  const tot   = document.getElementById('totalGeneral');

  if (!sel || !cInp || !uSpan || !pInp || !tabla || !tpl || !addBt || !tot) return;

  sel.addEventListener('change', () => {
    const o = sel.selectedOptions[0];
    uSpan.textContent = o.dataset.unidad || '';
    pInp.value        = o.dataset.precio || '';
  });

  addBt.addEventListener('click', () => {
    const o       = sel.selectedOptions[0];
    const idProd  = o?.value;
    const desc    = o?.dataset?.desc;
    const unidad  = o?.dataset?.unidad;
    const precio  = parseFloat(pInp.value);
    const cant    = parseFloat(cInp.value);

    if (!idProd)              return alert('Elegí un producto.');
    if (!cant || cant <= 0)   return alert('Cantidad inválida.');
    if (!precio || precio <= 0) return alert('Precio inválido.');

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

    sel.required = cInp.required = pInp.required = false;

    sel.selectedIndex = 0;
    cInp.value = '';
    uSpan.textContent = '';
    pInp.value = '';

    recalcularTotal();
  });

  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      recalcularTotal();

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
