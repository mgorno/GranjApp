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
    const tbody = document.querySelector('#tabla-detalle tbody');
    const tpl = document.getElementById('fila-template').content;
    const formNew = document.getElementById('formNuevoItem');
    const offcanvas = bootstrap.Offcanvas.getOrCreateInstance('#offNuevoItem');

    /* Añadir producto desde off‑canvas */
    formNew.addEventListener('submit', e => {
        e.preventDefault();
        const sel = document.getElementById('selProducto');
        const cant = document.getElementById('inpCantidad').value;
        const prec = document.getElementById('inpPrecio').value || sel.selectedOptions[0].dataset.precio;

        if (!sel.value) return;

        const fila = tpl.cloneNode(true);
        fila.querySelector('input[name="id_producto"]').value = sel.value;
        fila.querySelector('.nombre').textContent = sel.selectedOptions[0].dataset.desc;
        fila.querySelector('input[name="cantidad"]').value = cant || 1;
        fila.querySelector('input[name="precio"]').value = prec || '';

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

const tabla = document.getElementById('tabla-detalle').querySelector('tbody');
const tpl = document.getElementById('fila-template').content;
const addBtn = document.getElementById('agregar-fila');

addBtn.addEventListener('click', () => {
    tabla.appendChild(tpl.cloneNode(true));
});

tabla.addEventListener('click', e => {
    if (e.target.classList.contains('eliminar')) {
        e.target.closest('tr').remove();
    }
});

function actualizarUnidad(selectElement) {
    const unidad = selectElement.selectedOptions[0].dataset.unidad;
    const precio = selectElement.selectedOptions[0].dataset.precio;
    const fila = selectElement.closest('tr');
    fila.querySelector('.unidad-placeholder').innerText = unidad || '';

    const precioInput = fila.querySelector('input[name="precio"]');
    if (precio && !precioInput.value) {
        precioInput.value = precio;
    }
}

// Insertar una fila inicial al cargar
addBtn.click();
document.addEventListener('DOMContentLoaded', () => {
  const selProd   = document.getElementById('selProducto');
  const cantInput = document.getElementById('inpCantidad');
  const unidadLbl = document.getElementById('inpUnidad');
  const precioInp = document.getElementById('inpPrecio');
  const tabla     = document.querySelector('#tabla-detalle tbody');
  const tpl       = document.getElementById('fila-template')?.content;
  const addBtn    = document.getElementById('btnAddLinea');
  const totalLbl  = document.getElementById('totalGeneral');

  // Verificaciones básicas
  if (!selProd || !cantInput || !unidadLbl || !precioInp || !tabla || !tpl || !addBtn || !totalLbl) {
    console.error('Faltan elementos en el DOM para scripts.js');
    return;
  }

  // Al cambiar producto → actualiza unidad y precio
  selProd.addEventListener('change', () => {
    const opt = selProd.selectedOptions[0];
    unidadLbl.textContent = opt?.dataset.unidad || '';
    precioInp.value       = opt?.dataset.precio || '';
  });

  // Añadir línea
  addBtn.addEventListener('click', () => {
    const opt  = selProd.selectedOptions[0];
    const cant = Number(cantInput.value);
    const prec = Number(precioInp.value);

    if (!opt?.value || cant < 1 || prec <= 0) {
      alert('Completá producto, cantidad (>0) y precio (>0)');
      return;
    }

    const fila = tpl.cloneNode(true);
    fila.querySelector('input[name="id_producto"]').value  = opt.value;
    fila.querySelector('.nombre').textContent              = opt.dataset.desc;
    fila.querySelector('input[name="cantidad"]').value     = cant;
    fila.querySelector('input[name="unidad"]').value       = unidadLbl.textContent;
    fila.querySelector('.unidad-base').textContent         = unidadLbl.textContent;
    fila.querySelector('input[name="precio"]').value       = prec.toFixed(2);

    tabla.appendChild(fila);

    // Limpiar formulario de producto
    selProd.selectedIndex = 0;
    cantInput.value = '';
    unidadLbl.textContent = '';
    precioInp.value = '';

    actualizarTotal();
  });

  // Eliminar línea
  tabla.addEventListener('click', e => {
    if (e.target.closest('button.eliminar')) {
      e.target.closest('tr').remove();
      actualizarTotal();
    }
  });

  // Recalcular total
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
