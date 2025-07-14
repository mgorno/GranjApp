function enviarPorWhatsapp() {
  const {
    telefono,
    total_remito,
    saldo_anterior,
    saldo_total,
    id_remito,
    pdf_url
  } = window.REMITO_INFO;

  let tel = (telefono || "").replace(/\D/g, ""); // limpiar caracteres no numéricos
  if (!tel.startsWith("549")) {
    tel = "549" + tel;
  }

  const mensaje = `Hola, te comparto el remito #${id_remito}.\n` +
                  `Total remito: $${total_remito.toFixed(2)}\n` +
                  `Saldo anterior: $${saldo_anterior.toFixed(2)}\n` +
                  `Saldo total: $${saldo_total.toFixed(2)}\n` +
                  `Descargalo acá: ${window.location.origin + pdf_url}`;

  const texto = encodeURIComponent(mensaje);
  const url = `https://wa.me/${tel}?text=${texto}`;

  window.open(url, "_blank");
}
