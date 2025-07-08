(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return; // por si el script se carga en otra vista

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior || window.SALDO_ANTERIOR || 0);

  // Formatea número a $ 1.234,56
  const formatoPrecio = (num) => {
    return "$ " + num.toFixed(2).replace(".", ",");
  };

  // Actualiza el subtotal de una fila
  const actualizarSubtotalFila = (fila) => {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");
    // Convertir coma a punto para parsear
    const precio = parseFloat(precioInput.value.replace(",", ".")) || 0;
    const cantidad = parseFloat(cantidadInput.value.replace(",", ".")) || 0;
    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);
  };

  // Recalcula los totales del remito y saldo total
  const recalcularTotales = () => {
    let total = 0;
    tbody.querySelectorAll("tr").forEach((fila) => {
      const textoSubtotal = fila.querySelector(".subtotal-cell").textContent;
      // Quitar $ y espacio, cambiar coma por punto para parsear
      const subtotalNum = parseFloat(textoSubtotal.replace("$", "").trim().replace(",", ".")) || 0;
      total += subtotalNum;
    });
    totalRemitoEl.textContent = formatoPrecio(total);
    saldoTotalEl.textContent = formatoPrecio(total + saldoAnterior);
  };

  // Crea una fila vacía para agregar
  const crearFilaVacia = () => {
    const tr = document.createElement("tr");
    // Copiar opciones del select original para mantener productos
    const opciones = document.querySelector(".producto-select")?.innerHTML || "";

    tr.innerHTML = `
      <td>
        <select name="producto_id[]" class="form-select producto-select" required>
          ${opciones}
        </select>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="precio[]" value="0,00" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="cantidad_real[]" value="0,00" class="form-control text-end table-input cantidad-input" required>
      </td>
      <td class="text-end subtotal-cell">$ 0,00</td>
      <td class="text-center">
        <button type="button" class="btn btn-outline-danger btn-sm eliminar-fila" title="Eliminar fila">
          <i class="bi bi-trash"></i>
        </button>
      </td>
    `;

    const select = tr.querySelector(".producto-select");
    if (select) select.value = "";

    return tr;
  };

  // Formatear subtotales actuales al cargar
  tbody.querySelectorAll("tr").forEach(fila => actualizarSubtotalFila(fila));
  recalcularTotales();

  // Eventos delegados en tbody
  tbody.addEventListener("input", (e) => {
    if (e.target.classList.contains("precio-input") || e.target.classList.contains("cantidad-input")) {
      // Reemplazar coma por punto en inputs para evitar errores al parsear
      e.target.value = e.target.value.replace(",", ".");
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
      precioInput.value = parseFloat(option.dataset.precio || 0).toFixed(2).replace(".", ",");
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

  const btnAgregarFila = document.getElementById("agregar-fila");
  if (btnAgregarFila) {
    btnAgregarFila.addEventListener("click", () => {
      const nuevaFila = crearFilaVacia();
      tbody.appendChild(nuevaFila);
      recalcularTotales();
    });
  }
})();
