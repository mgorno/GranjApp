  const telefono = "{{ telefono|default('')|replace(' ', '')|replace('(', '')|replace(')', '')|replace('-', '') }}";
  const total_remito = {{ total_remito|default(0)|round(2) }};
  const saldo_anterior = {{ saldo_anterior|default(0)|round(2) }};
  const saldo_total = {{ saldo_total|default(0)|round(2) }};

  function enviarPorWhatsapp() {
    // Limpiar el teléfono y agregar prefijo 549 si no está
    let tel = telefono.replace(/\D/g, '');
    if (!tel.startsWith('549')) {
      tel = '549' + tel;
    }

    const pdfUrl = window.location.origin + "{{ url_for('entregas.remito_pdf', id_remito=id_remito) }}";

    const mensaje = `Hola, te comparto el remito #{{ id_remito }}.\n` +
                    `Total remito: $${total_remito.toFixed(2)}\n` +
                    `Saldo anterior: $${saldo_anterior.toFixed(2)}\n` +
                    `Saldo total: $${saldo_total.toFixed(2)}\n` +
                    `Descargalo acá: ${pdfUrl}`;

    const texto = encodeURIComponent(mensaje);

    window.open(`https://wa.me/${tel}?text=${texto}`, '_blank');
  }