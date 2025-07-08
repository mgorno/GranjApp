(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return;

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");

  // Parsear saldo anterior con formato argentino
  const saldoAnterior = parseFloat(
    (form?.dataset?.saldoAnterior || "0")
      .replace(/\./g, "")
      .replace(",", ".")
  ) || 0;

  // 👉 Formatea número con separador de miles y decimales (coma)
  const formatoArg = (num, decimales = 2) => {
    return num
      .toFixed(decimales)
      .replace(".", ",")
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };

  const formatoPrecio = (num) => "$ " + formatoArg(num, 0); // precios sin decimales
  const formatoCantidad = (num) => formatoArg(num, 3).replace(/,?0+$/, "").replace(/,$/, "");

  // Actualiza el subtotal de una fila
  const actualizarSubtotalFila = (fila) => {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");

    const precio = parseFloat(precioInput.value.replace(/\./g, "").replace(",", ".")) || 0;
    const cantidad = parseFloat(cantidadInput.value.replace(/\./g, "").replace(",", ".")) || 0;

    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);
  };

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

  // Crea una fila vacía para agregar
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
        <input type="text" name="precio[]" value="0" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="text" name="cantidad_real[]" value="0" class="form-control text-end table-input cantidad-input" required>
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

  // Inicializa
  tbody.querySelectorAll("tr").forEach((fila) => actualizarSubtotalFila(fila));
  recalcularTotales();

  // Escuchar cambios en inputs
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
      precioInput.value = parseFloat(option.dataset.precio || 0).toFixed(0);
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
