(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return;

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior?.replace(",", ".") || 0);

  // ✅ Formato tipo: "$ 1.234.567"
  const formatoPrecio = (num) => {
    return "$ " + Math.round(num).toLocaleString("es-AR");
  };

  // ✅ Formato tipo: "1", "1,2", "1,121"
const formatoCantidad = (num) => {
  const redondeado = parseFloat(num).toFixed(3); // 3 decimales como máximo
  const limpio = redondeado.replace(/\.?0+$/, ""); // elimina ceros innecesarios
  return limpio.replace(".", ",");
};


  const actualizarSubtotalFila = (fila) => {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");

    const precio = parseFloat(precioInput.value.toString().replace(",", ".")) || 0;
    const cantidad = parseFloat(cantidadInput.value.toString().replace(",", ".")) || 0;
    const subtotal = precio * cantidad;

    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);
  };

  const recalcularTotales = () => {
    let total = 0;
    tbody.querySelectorAll("tr").forEach((fila) => {
      const textoSubtotal = fila.querySelector(".subtotal-cell").textContent;
      const subtotalNum = parseFloat(
        textoSubtotal.replace("$", "").trim().replace(/\./g, "").replace(",", ".")
      ) || 0;
      total += subtotalNum;
    });

    totalRemitoEl.textContent = formatoPrecio(total);
    saldoTotalEl.textContent = formatoPrecio(total + saldoAnterior);
  };

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
        <input type="number" step="1" name="precio[]" value="0" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="number" step="0.001" name="cantidad_real[]" value="0,00" class="form-control text-end table-input cantidad-input" required>
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

  // Inicializar subtotales al cargar
tbody.querySelectorAll("tr").forEach((fila) => {
  const precioInput = fila.querySelector(".precio-input");
  const cantidadInput = fila.querySelector(".cantidad-input");

  const precio = parseFloat(precioInput.value.replace(",", ".")) || 0;
  const cantidad = parseFloat(cantidadInput.value.replace(",", ".")) || 0;

  // Actualizamos valores formateados en inputs
  precioInput.value = Math.round(precio);
  cantidadInput.value = formatoCantidad(cantidad);

  actualizarSubtotalFila(fila);
});

  // Cambiar producto
  tbody.addEventListener("change", (e) => {
    if (e.target.classList.contains("producto-select")) {
      const fila = e.target.closest("tr");
      const precioInput = fila.querySelector(".precio-input");
      const option = e.target.selectedOptions[0];
      const precio = parseFloat(option.dataset.precio || 0);
      precioInput.value = Math.round(precio);
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  // Eliminar fila
  tbody.addEventListener("click", (e) => {
    const btn = e.target.closest(".eliminar-fila");
    if (btn) {
      btn.closest("tr").remove();
      recalcularTotales();
    }
  });

  // Agregar fila vacía
  const btnAgregarFila = document.getElementById("agregar-fila");
  if (btnAgregarFila) {
    btnAgregarFila.addEventListener("click", () => {
      const nuevaFila = crearFilaVacia();
      tbody.appendChild(nuevaFila);
      recalcularTotales();
    });
  }
})();
