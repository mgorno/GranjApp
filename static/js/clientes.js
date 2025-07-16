document.addEventListener('DOMContentLoaded', () => {
  // === Buscador ===
  const input = document.getElementById('buscarCliente');
  if (input) {
    input.addEventListener('input', () => {
      const filtro = input.value.toLowerCase();
      const clientes = document.querySelectorAll('.list-group > .list-group-item');

      clientes.forEach(cliente => {
        const nombre = cliente.querySelector('.flex-grow-1')?.textContent.toLowerCase();
        const detalle = cliente.nextElementSibling;
        const coincide = nombre.includes(filtro);

        cliente.style.display = coincide ? '' : 'none';
        if (detalle) detalle.style.display = coincide ? '' : 'none';
      });
    });
  }

  // === Flechas colapsables con rotación ===
  document.querySelectorAll('.btn-toggle-arrow').forEach(button => {
    const targetSelector = button.getAttribute('data-bs-target');
    const collapseEl = document.querySelector(targetSelector);

    if (!collapseEl) return;

    button.addEventListener('click', () => {
      const isShown = collapseEl.classList.contains('show');
      button.style.transform = isShown ? 'rotate(0deg)' : 'rotate(90deg)';
    });

    collapseEl.addEventListener('shown.bs.collapse', () => {
      button.style.transform = 'rotate(90deg)';
    });

    collapseEl.addEventListener('hidden.bs.collapse', () => {
      button.style.transform = 'rotate(0deg)';
    });

    // Estado inicial
    if (collapseEl.classList.contains('show')) {
      button.style.transform = 'rotate(90deg)';
    }
  });

  // === Botón editar campos ===
  document.querySelectorAll('.btn-editar-campos').forEach(btn => {
    btn.addEventListener('click', () => {
      const form = btn.closest('form');
      if (!form) return;

      form.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.type === 'checkbox') {
          el.removeAttribute('disabled');
        } else {
          el.removeAttribute('readonly');
        }
      });

      btn.classList.add('d-none');
      form.querySelector('.btn-guardar')?.classList.remove('d-none');
      form.querySelector('.btn-cancelar')?.classList.remove('d-none');
    });
  });

  // === Botón cancelar edición ===
  document.querySelectorAll('.btn-cancelar').forEach(btn => {
    btn.addEventListener('click', () => {
      const form = btn.closest('form');
      if (!form) return;

      form.reset();

      form.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.type === 'checkbox') {
          el.setAttribute('disabled', '');
        } else {
          el.setAttribute('readonly', '');
        }
      });

      form.querySelector('.btn-editar-campos')?.classList.remove('d-none');
      form.querySelector('.btn-guardar')?.classList.add('d-none');
      form.querySelector('.btn-cancelar')?.classList.add('d-none');
    });
  });

  // === (Opcional) Edición inline de campos individuales ===
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

  // === Reset de campos inline al cerrar el accordion ===
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

  // === Envío del formulario de nuevo cliente ===
  const formNuevo = document.getElementById("formNuevoCliente");
  if (formNuevo) {
    const btnGuardar = formNuevo.querySelector("button[type='submit']");
    const spinner = document.getElementById("spinnerCliente");
    const texto = document.getElementById("textoBotonCliente");

    formNuevo.addEventListener("submit", async (e) => {
      e.preventDefault();

      btnGuardar.disabled = true;
      spinner?.classList.remove("d-none");
      if (texto) texto.textContent = "Procesando...";

      const formData = new FormData(formNuevo);

      const response = await fetch(formNuevo.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      });

      if (response.ok) {
        const offcanvasEl = document.getElementById("offNuevoCliente");
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();

        setTimeout(() => location.reload(), 500);
      } else {
        alert("Ocurrió un error al guardar el cliente.");
        btnGuardar.disabled = false;
        spinner?.classList.add("d-none");
        if (texto) texto.innerHTML = `<i class="bi bi-save2 me-1"></i>Guardar Cliente`;
      }
    });
  }
});
