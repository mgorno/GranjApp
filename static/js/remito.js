(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return; // por si el script se carga en otra vista

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior || window.SALDO_ANTERIOR || 0);

  // ---- Helpers ----
  const actualizarSubtotalFila = (fila) => {
    const precio = parseFloat(fila.querySelector(".precio-input").value) || 0;
    const cantidad = parseFloat(fila.querySelector(".cantidad-input").value) || 0;
    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = subtotal.toFixed(2);
  };

  const recalcularTotales = () => {
    let total = 0;
    tbody.querySelectorAll("tr").forEach((fila) => {
      total += parseFloat(fila.querySelector(".subtotal-cell").textContent) || 0;
    });
    totalRemitoEl.textContent = total.toFixed(2);
    saldoTotalEl.textContent = (total + saldoAnterior).toFixed(2);
  };

  const crearFilaVacia = () => {
    const tr = document.createElement("tr");
    const opciones = document.querySelector(".producto-select")?.innerHTML || "";

    tr.innerHTML = `
      <td>
        <select name="producto_id" class="form-select producto-select" required>
          ${opciones}
        </select>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="precio" value="0.00" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="cantidad_real" value="0.00" class="form-control text-end table-input cantidad-input" required>
      </td>
      <td class="text-end subtotal-cell">0.00</td>
      <td class="text-center">
        <button type="button" class="btn btn-outline-danger btn-sm eliminar-fila"><i class="bi bi-trash"></i></button>
      </td>
    `;

    const select = tr.querySelector(".producto-select");
    if (select) select.value = "";
    return tr;
  };

  // ---- Iniciar ----
  recalcularTotales();

  // ---- Event delegation ----
  tbody.addEventListener("input", (e) => {
    if (e.target.classList.contains("precio-input") || e.target.classList.contains("cantidad-input")) {
      const fila = e.target.closest("tr");
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  tbody.addEventListener("change", (e) => {
    if (e.target.classList.contains("producto-select")) {
      const fila = e.target.closest("tr");
      const precioInput = fila.querySelector(".precio-input");
      const option = e.target.selectedOptions[0];
      precioInput.value = parseFloat(option.dataset.precio || 0).toFixed(2);
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  tbody.addEventListener("click", (e) => {
    const btn = e.target.closest(".eliminar-fila");
    if (btn) {
      btn.closest("tr").remove();
      recalcularTotales();
    }
  });

  document.getElementById("agregar-fila").addEventListener("click", () => {
    const nuevaFila = crearFilaVacia();
    tbody.appendChild(nuevaFila);
  });
})();
