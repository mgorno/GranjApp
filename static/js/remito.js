(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return;

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior || 0);

  // Formatea número como moneda argentina sin decimales
  const formatoPrecio = (num) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  // Calcula el subtotal de una fila
  const actualizarSubtotalFila = (fila) => {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");

    const precio = parseFloat(precioInput.value.replace(",", ".").replace(/\./g, "")) || 0;
    const cantidad = parseFloat(cantidadInput.value.replace(",", ".")) || 0;

    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);
  };

  // Recalcula el total del remito y el saldo total
  const recalcularTotales = () => {
    let total = 0;

    tbody.querySelectorAll("tr").forEach((fila) => {
      const textoSubtotal = fila.querySelector(".subtotal-cell").textContent;
      const subtotalNum = parseFloat(
        textoSubtotal.replace(/\./g, "").replace(",", ".").replace("$", "").trim()
      ) || 0;
      total += subtotalNum;
    });

    totalRemitoEl.textContent = formatoPrecio(total);
    saldoTotalEl.textContent = formatoPrecio(total + saldoAnterior);
  };

  // Crea una fila nueva vacía
  const crearFilaVacia = () => {
    const tr = document.createElement("tr");
    const opciones = document.querySelector(".producto-select")?.innerHTML || "";

    tr.innerHTML = `
      <td>
        <select name="producto_id[]" class="form-select producto-select" required>
          ${opciones}
        </select>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="precio[]" value="0" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="number" step="0.01" name="cantidad_real[]" value="0" class="form-control text-end table-input cantidad-input" required>
      </td>
      <td class="text-end subtotal-cell">$ 0</td>
      <td class="text-center">
        <button type="button" class="btn btn-outline-danger btn-sm eliminar-fila" title="Eliminar fila">
          <i class="bi bi-trash"></i>
        </button>
      </td>
    `;
    return tr;
  };

  // Iniciar: formatear subtotales existentes
  tbody.querySelectorAll("tr").forEach(fila => {
    actualizarSubtotalFila(fila);
  });
  recalcularTotales();

  // Eventos de cambio de inputs
  tbody.addEventListener("input", (e) => {
    if (e.target.classList.contains("precio-input") || e.target.classList.contains("cantidad-input")) {
      const fila = e.target.closest("tr");
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  // Cambio de producto
  tbody.addEventListener("change", (e) => {
    if (e.target.classList.contains("producto-select")) {
      const fila = e.target.closest("tr");
      const precioInput = fila.querySelector(".precio-input");
      const option = e.target.selectedOptions[0];
      const precio = parseFloat(option.dataset.precio || 0);
      precioInput.value = precio;
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  // Botón eliminar fila
  tbody.addEventListener("click", (e) => {
    const btn = e.target.closest(".eliminar-fila");
    if (btn) {
      btn.closest("tr").remove();
      recalcularTotales();
    }
  });

  // Botón agregar fila
  const btnAgregarFila = document.getElementById("agregar-fila");
  if (btnAgregarFila) {
    btnAgregarFila.addEventListener("click", () => {
      const nuevaFila = crearFilaVacia();
      tbody.appendChild(nuevaFila);
    });
  }
})();
