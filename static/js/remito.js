(() => {
  const tabla = document.getElementById("tabla-remito");
  if (!tabla) return; // si no está la tabla, salir

  const form = document.getElementById("form-remito");
  const tbody = tabla.querySelector("tbody");
  const totalRemitoEl = document.getElementById("total-remito");
  const saldoTotalEl = document.getElementById("saldo-total");
  const saldoAnterior = parseFloat(form?.dataset?.saldoAnterior || window.SALDO_ANTERIOR || 0);

  // Formatea número a cantidad con miles y coma decimal (hasta 3 decimales)
  function formatoCantidad(num) {
    if (num === 0) return "0";
    const entero = Math.trunc(num);
    const decimales = Math.abs(num - entero);
    const enteroStr = entero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    if (decimales === 0) return enteroStr;
    let decStr = decimales.toFixed(3).substring(2).replace(/0+$/, "");
    return enteroStr + (decStr ? "," + decStr : "");
  }

  // Formatea número a precio: "$ 1.234"
  function formatoPrecio(num) {
    const entero = Math.floor(num);
    const enteroStr = entero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return `$ ${enteroStr}`;
  }

  // Actualiza el subtotal de una fila y formatea inputs
  function actualizarSubtotalFila(fila) {
    const precioInput = fila.querySelector(".precio-input");
    const cantidadInput = fila.querySelector(".cantidad-input");

    // Parsear valores: reemplazar puntos miles y coma decimal a punto decimal JS
   const precio = parseFloat(precioInput.value) || 0;
   const cantidad = parseFloat(cantidadInput.value) || 0;

    const subtotal = precio * cantidad;
    fila.querySelector(".subtotal-cell").textContent = formatoPrecio(subtotal);

    // Formatear inputs para mostrar correctamente
    cantidadInput.value = formatoCantidad(cantidad);
    // Precio solo parte entera formateada con puntos
    precioInput.value = parseFloat(option.dataset.precio || 0).toFixed(0);;
  }

  // Recalcula totales y actualiza visualización
  function recalcularTotales() {
    let total = 0;
    tbody.querySelectorAll("tr").forEach((fila) => {
      const textoSubtotal = fila.querySelector(".subtotal-cell").textContent;
      // Quitar signo $, puntos miles y reemplazar coma decimal a punto JS
      const subtotalNum = parseFloat(textoSubtotal.replace("$", "").replace(/\./g, "").replace(",", ".")) || 0;
      total += subtotalNum;
    });
    totalRemitoEl.textContent = formatoPrecio(total);
    saldoTotalEl.textContent = formatoPrecio(total + saldoAnterior);
  }

  // Crear una fila vacía para agregar
  function crearFilaVacia() {
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
  }

  // Inicializar subtotales y totales al cargar
  tbody.querySelectorAll("tr").forEach(fila => actualizarSubtotalFila(fila));
  recalcularTotales();

  // Eventos delegados en tbody
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
      const precioOpt = parseFloat(option.dataset.precio || 0);
      precioInput.value = Math.floor(precioOpt).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
      actualizarSubtotalFila(fila);
      recalcularTotales();
    }
  });


})();
