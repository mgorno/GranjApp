document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('buscarCliente');

    input.addEventListener('input', () => {
        const filtro = input.value.toLowerCase();
        const clientes = document.querySelectorAll('.nombre-cliente');

        clientes.forEach(cliente => {
            const nombre = cliente.querySelector('div').textContent.toLowerCase();
            const idCollapse = cliente.querySelector('a').getAttribute('href');
            const detalle = document.querySelector(idCollapse);

            if (nombre.includes(filtro)) {
                cliente.style.display = '';
                if (detalle) detalle.style.display = '';
            } else {
                cliente.style.display = 'none';
                if (detalle) detalle.style.display = 'none';
            }
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

