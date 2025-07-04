document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn-editar-campo').forEach(btn => {
    btn.addEventListener('click', () => {
      const wrapper = btn.closest('.d-flex');
      const input   = wrapper.querySelector('input');
      const span    = wrapper.querySelector('.valor-campo');
      if (!input || !span) return;

      input.classList.toggle('d-none');
      span.classList.toggle('d-none');

      if (!input.classList.contains('d-none')) input.focus();
    });
  });
});
