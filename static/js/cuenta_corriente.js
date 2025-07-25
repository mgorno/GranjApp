document.addEventListener('DOMContentLoaded', () => {
  // Buscador
  const input = document.getElementById('buscarCliente');
  if (input) {
    input.addEventListener('input', () => {
      const filtro = input.value.toLowerCase();
      const clientes = document.querySelectorAll('.list-group > .list-group-item');

      clientes.forEach(cliente => {
        const nombre = cliente.querySelector('.flex-grow-1 strong').textContent.toLowerCase();
        const detalle = cliente.nextElementSibling;
        const coincide = nombre.includes(filtro);

        cliente.style.display = coincide ? '' : 'none';
        if (detalle) detalle.style.display = coincide ? '' : 'none';
      });
    });
  }

  // Botón editar por campo
  document.querySelectorAll('.btn-editar-campo').forEach(btn => {
    btn.addEventListener('click', () => {
      const parent = btn.closest('.d-flex.align-items-center.gap-2');
      if (!parent) return;

      const span = parent.querySelector('.valor-campo');
      const input = parent.querySelector('input');

      if (span && input) {
        span.classList.add('d-none');
        input.classList.remove('d-none');
        input.focus();
        btn.classList.add('d-none');
      }
    });
  });

  // Al cerrar un collapse, restaurar campos en modo lectura
  document.querySelectorAll('.accordion-collapse').forEach(collapse => {
    collapse.addEventListener('hidden.bs.collapse', () => {
      const inputs = collapse.querySelectorAll('input:not(.d-none)');
      inputs.forEach(input => {
        const parent = input.closest('.d-flex.align-items-center.gap-2');
        if (!parent) return;
        const span = parent.querySelector('.valor-campo');
        const btn = parent.querySelector('.btn-editar-campo');

        if (span && btn) {
          input.classList.add('d-none');
          span.classList.remove('d-none');
          btn.classList.remove('d-none');
        }
      });
    });
  });

  // Guardar cliente - botón "Procesando…" y cierre automático
  const formNuevo = document.getElementById("formNuevoCliente");
  if (formNuevo) {
    const btnGuardar = formNuevo.querySelector("button[type='submit']");

    formNuevo.addEventListener("submit", async (e) => {
      e.preventDefault();

      btnGuardar.disabled = true;
      btnGuardar.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Procesando...`;

      const formData = new FormData(formNuevo);

      const response = await fetch(formNuevo.action, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const offcanvasEl = document.getElementById("offNuevoCliente");
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();

        setTimeout(() => location.reload(), 500);  // recarga la lista
      } else {
        alert("Ocurrió un error al guardar el cliente.");
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = `<i class="bi bi-save2 me-1"></i>Guardar Cliente`;
      }
    });
  }
});
