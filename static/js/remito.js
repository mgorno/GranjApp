(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return; // por si el script se carga en otra vista

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior || window.SALDO_ANTERIOR || 0);

  // Formatea número a $ 1.234 (sin decimales, punto como separador de miles)
  const formatoPrecio = (num) => {
    const esNegativo = num < 0;
    const valor = Math.abs(num)
      .toFixed(0)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return (esNegativo ? "-$ " : "$ ") + valor;
  };


  // Formatea cantidad con hasta 3 decimales, usa coma decimal y punto miles
  const formatoCantidad = (num) => {
    let parts = num.toString().split(".");
    let integerPart = parts[0];
    let decimalPart = parts[1] ? parts[1].substring(0, 3) : "";

    // Formatear parte entera con puntos
    integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

    if (decimalPart.length > 0) {
      return integerPart + "," + decimalPart;
    }
    return integerPart;
  };

  // Actualiza el subtotal de una fila
  const actualizarSubtotalFila = (fila) => {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");

    // Convertir valor numérico directamente (inputs type=number ya tienen punto decimal)
    const precio = Number(precioInput.value) || 0;
    const cantidad = Number(cantidadInput.value) || 0;

    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);
  };

  // Recalcula totales del remito y saldo total
  const recalcularTotales = () => {
    let total = 0;
    tbody.querySelectorAll("tr").forEach((fila) => {
      const textoSubtotal = fila.querySelector(".subtotal-cell").textContent;
      // Quitar $ y espacios, quitar puntos, cambiar coma por punto para parsear
      const subtotalNum = parseFloat(
        textoSubtotal
          .replace("$", "")
          .replace(/\./g, "")
          .replace(",", ".")
          .trim()
      ) || 0;
      total += subtotalNum;
    });
    totalRemitoEl.textContent = formatoPrecio(total);         
    saldoTotalEl.textContent = formatoPrecio(saldoAnterior + total);
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
        <input type="number" step="1" name="precio[]" value="0" class="form-control text-end table-input precio-input" required>
      </td>
      <td class="text-end">
        <input type="number" step="0.001" name="cantidad_real[]" value="0" class="form-control text-end table-input cantidad-input" required>
      </td>
      <td class="text-end subtotal-cell">$ 0</td>
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
      const fila = e.target.closest("tr");

      // Opcional: formatear cantidad en el input con formato argentino
      // pero cuidado, inputs type=number no permiten comas, así que mejor no formatear aquí

      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });

  tbody.addEventListener("change", (e) => {
    if (e.target.classList.contains("producto-select")) {
      const fila = e.target.closest("tr");
      const precioInput = fila.querySelector(".precio-input");
      const option = e.target.selectedOptions[0];
      precioInput.value = Math.round(Number(option.dataset.precio || 0));
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
