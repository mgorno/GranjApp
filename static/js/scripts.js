document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('buscarCliente');

    input.addEventListener('input', () => {
        const filtro = input.value.toLowerCase();
        const clientes = document.querySelectorAll('.cliente-item');

        clientes.forEach(cliente => {
            const nombre = cliente.querySelector('.nombre-cliente').textContent.toLowerCase();
            const idCollapse = cliente.querySelector('a').getAttribute('href');
            const detalle = document.querySelector(idCollapse);

            const coincide = nombre.includes(filtro);

            cliente.style.display = coincide ? '' : 'none';
            if (detalle) detalle.style.display = coincide ? '' : 'none';
        });
    });
});



document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-editar-campo').forEach(btn => {
        btn.addEventListener('click', () => {
            const wrapper = btn.closest('.d-flex');
            const input = wrapper.querySelector('input');
            const span = wrapper.querySelector('.valor-campo');

            // Alternar visibilidad
            input.classList.toggle('d-none');
            span.classList.toggle('d-none');

            // Poner foco en el input si se está editando
            if (!input.classList.contains('d-none')) {
                input.focus();
            }
        });
    });
});

