(function () {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }

  function iniciar() {
    // Buscador
    const input = document.getElementById("buscarProducto");
    if (input) {
      input.addEventListener("input", () => {
        const filtro = input.value.toLowerCase();
        const productos = document.querySelectorAll(".list-group > .list-group-item");

        productos.forEach(producto => {
          const nombre = producto.querySelector(".flex-grow-1 strong").textContent.toLowerCase();
          const detalle = producto.nextElementSibling;
          const coincide = nombre.includes(filtro);
          producto.style.display = coincide ? "" : "none";
          if (detalle) detalle.style.display = coincide ? "" : "none";
        });
      });
    }

    // Envío del formulario nuevo producto
    const formNuevo = document.getElementById("formNuevoProducto");
    if (formNuevo) {
      const btnGuardar = formNuevo.querySelector("button[type='submit']");
      const spinner = document.getElementById("spinnerProducto");
      const texto = document.getElementById("textoBotonProducto");

      formNuevo.addEventListener("submit", async (e) => {
        e.preventDefault();
        btnGuardar.disabled = true;
        spinner.classList.remove("d-none");
        texto.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Procesando...';

        const formData = new FormData(formNuevo);

        const response = await fetch(formNuevo.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest"
          }
        });

        if (response.ok) {
          const offcanvasEl = document.getElementById("offNuevoProducto");
          const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
          if (bsOffcanvas) bsOffcanvas.hide();
          setTimeout(() => location.reload(), 500);
        } else {
          alert("El producto ya existe o hay un error en los datos.");
          btnGuardar.disabled = false;
          spinner.classList.add("d-none");
          texto.innerHTML = '<i class="bi bi-save2 me-1"></i>Guardar Producto';
        }
      });
    }

    // Flechitas que giran en collapse
    document.querySelectorAll('.btn-toggle-arrow').forEach(button => {
      const icon = button.querySelector('i');
      const targetSelector = button.getAttribute('data-bs-target');
      const collapseEl = document.querySelector(targetSelector);

      // Al hacer clic
      button.addEventListener('click', () => {
        const isShown = collapseEl.classList.contains('show');
        button.style.transform = isShown ? 'rotate(0deg)' : 'rotate(90deg)';
      });

      // Cuando se muestra el collapse
      collapseEl.addEventListener('shown.bs.collapse', () => {
        button.style.transform = 'rotate(90deg)';
      });

      // Cuando se oculta
      collapseEl.addEventListener('hidden.bs.collapse', () => {
        button.style.transform = 'rotate(0deg)';
      });

      // Estado inicial
      if (collapseEl.classList.contains('show')) {
        button.style.transform = 'rotate(90deg)';
      }
    });
  }
})();
