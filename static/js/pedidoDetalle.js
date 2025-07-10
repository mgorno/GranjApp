document.addEventListener("DOMContentLoaded", () => {
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
  const sel = document.getElementById("selProducto");
  const cInp = document.getElementById("inpCantidad");
  const uSpan = document.getElementById("inpUnidad");
  const pInp = document.getElementById("inpPrecio");
  const tabla = document.querySelector("#tabla-detalle tbody");
  const tpl = document.getElementById("fila-template").content;
  const addBt = document.getElementById("btnAddLinea");
  const tot = document.getElementById("totalGeneral");

  if (!sel || !cInp || !uSpan || !pInp || !tabla || !tpl || !addBt || !tot) return;

  // --- Función de formato de cantidad ---
  function formatearCantidad(valor) {
    const esEntero = Number.isInteger(valor);
    if (esEntero) {
      return valor.toLocaleString("es-AR");
    } else {
      const partes = valor.toFixed(3).split(".");
      const parteEntera = parseInt(partes[0]).toLocaleString("es-AR");
      const parteDecimal = partes[1];
      return `${parteEntera},${parteDecimal}`;
    }
  }

  sel.addEventListener("change", () => {
    const o = sel.selectedOptions[0];
    uSpan.textContent = o.dataset.unidad || "";
    pInp.value = o.dataset.precio || "";
  });

  addBt.addEventListener("click", () => {
    const o = sel.selectedOptions[0];
    const idProd = o?.value;
    const desc = o?.dataset?.desc;
    const unidad = o?.dataset?.unidad;
    const precio = parseFloat(pInp.value.replace(",", "."));
    const cant = parseFloat(cInp.value.replace(",", "."));

    if (!idProd) {
      alert("Elegí un producto.");
      return;
    }
    if (!cant || cant <= 0) {
      alert("Cantidad inválida. Debe ser mayor a 0.");
      return;
    }
    if (!precio || precio <= 0) {
      alert("Precio inválido. Debe ser mayor a 0.");
      return;
    }

    if ([...tabla.querySelectorAll('input[name="id_producto"]')].some(input => input.value === idProd)) {
      alert("Ese producto ya está en al detalle.");
      return;
    }

    const fila = tpl.cloneNode(true);

    const cantidadTexto = formatearCantidad(cant);
    const precioTexto = `$ ${Math.round(precio).toLocaleString("es-AR")}`;
    const subtotal = Math.round(precio * cant);
    const subtotalTexto = `$ ${subtotal.toLocaleString("es-AR")}`;

    fila.querySelector('input[name="id_producto"]').value = idProd;
    fila.querySelector(".nombre").textContent = desc;
    fila.querySelector('input[name="cantidad"]').value = cant;
    fila.querySelector(".cantidad").textContent = cantidadTexto;
    fila.querySelector('input[name="unidad"]').value = unidad;
    fila.querySelector(".unidad-base").textContent = unidad;
    fila.querySelector('input[name="precio"]').value = Math.round(precio);
    fila.querySelector(".precio").textContent = precioTexto;
    fila.querySelector('input[name="subtotal"]').value = subtotal;
    fila.querySelector(".subtotal").textContent = subtotalTexto;

    tabla.appendChild(fila);

    sel.required = cInp.required = pInp.required = false;
    sel.selectedIndex = 0;
    cInp.value = "";
    uSpan.textContent = "";
    pInp.value = "";

    recalcularTotal();
  });

  tabla.addEventListener("click", (e) => {
    if (e.target.closest("button.eliminar")) {
      e.target.closest("tr").remove();
      recalcularTotal();

      if (tabla.querySelectorAll("tr").length === 0) {
        sel.required = cInp.required = pInp.required = true;
      }
    }
  });

  function recalcularTotal() {
    let suma = 0;
    tabla.querySelectorAll("tr").forEach(tr => {
      const c = parseFloat(tr.querySelector('input[name="cantidad"]').value) || 0;
      const p = parseFloat(tr.querySelector('input[name="precio"]').value) || 0;
      suma += c * p;
    });
    tot.textContent = Math.round(suma).toLocaleString("es-AR");
  }
});
