(function() {
  const tabla = document.getElementById('tabla-remito');
  const tbody = tabla.querySelector('tbody');
  const totalRemitoEl = document.getElementById('total-remito');
  const saldoAnterior = parseFloat('{{ saldo_anterior }}');
  const saldoTotalEl = document.getElementById('saldo-total');

  // Calcula totales al iniciar
  recalcularTotales();

  // Delegación de eventos
  tbody.addEventListener('input', function(e) {
    if (e.target.classList.contains('precio-input') || e.target.classList.contains('cantidad-input')) {
      const fila = e.target.closest('tr');
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  tbody.addEventListener('change', function(e) {
    if (e.target.classList.contains('producto-select')) {
      const fila = e.target.closest('tr');
      const precioInput = fila.querySelector('.precio-input');
      const option = e.target.selectedOptions[0];
      precioInput.value = parseFloat(option.dataset.precio).toFixed(2);
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  tbody.addEventListener('click', function(e) {
    if (e.target.closest('.eliminar-fila')) {
      e.target.closest('tr').remove();
      recalcularTotales();
    }
  });

  // Agregar filas
  document.getElementById('agregar-fila').addEventListener('click', function() {
    const nuevaFila = crearFilaVacia();
    tbody.appendChild(nuevaFila);
  });

  function crearFilaVacia() {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <select name="producto_id" class="form-select producto-select" required>
          <option value="" selected disabled>Seleccione…</option>
          {% for p in productos %}
          <option value="{{ p.id }}" data-precio="{{ '%.2f'|format(p.precio) }}" data-unidad="{{ p.unidad }}">{{ p.descripcion }} ({{ p.unidad }})</option>
          {% endfor %}
        </select>
      </td>
      <td class="text-end"><input type="number" step="0.01" name="precio" value="0.00" class="form-control text-end table-input precio-input" required></td>
      <td class="text-end"><input type="number" step="0.01" name="cantidad_real" value="0.00" class="form-control text-end table-input cantidad-input" required></td>
      <td class="text-end subtotal-cell">0.00</td>
      <td class="text-center"><button type="button" class="btn btn-outline-danger btn-sm eliminar-fila"><i class="bi bi-trash"></i></button></td>`;
    return tr;
  }

  function actualizarSubtotalFila(fila) {
    const precio = parseFloat(fila.querySelector('.precio-input').value) || 0;
    const cantidad = parseFloat(fila.querySelector('.cantidad-input').value) || 0;
    const subtotal = precio * cantidad;
    fila.querySelector('.subtotal-cell').textContent = subtotal.toFixed(2);
  }

  function recalcularTotales() {
    let total = 0;
    tbody.querySelectorAll('tr').forEach(fila => {
      const subtotal = parseFloat(fila.querySelector('.subtotal-cell').textContent) || 0;
      total += subtotal;
    });
    totalRemitoEl.textContent = total.toFixed(2);
    saldoTotalEl.textContent = (total + saldoAnterior).toFixed(2);
  }
})();