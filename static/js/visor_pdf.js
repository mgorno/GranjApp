function enviarPorWhatsapp() {
  const {
    telefono,
    total_remito,
    saldo_anterior,
    saldo_total,
    id_remito,
    pdf_url
  } = window.REMITO_INFO;

  let tel = (telefono || "").replace(/\D/g, "");
  if (!tel.startsWith("549")) {
    tel = "549" + tel;
  }

  const formatoPesos = n => n.toLocaleString('es-AR'); 

  const mensaje = `Buenas! Envío remito N.º ${id_remito} correspondiente a tu compra.\n\n` +
                  `📄 Total del remito: $${formatoPesos(total_remito)}\n` +
                  `💰 Saldo anterior: $${formatoPesos(saldo_anterior)}\n` +
                  `🧾 Saldo total actualizado: $${formatoPesos(saldo_total)}\n\n` +
                  `Podés descargar el remito desde el siguiente link:\n${window.location.origin + pdf_url}\n\n` +
                  `En un rato vamos a estar por ahí dejándote la mercadería.`;

  const texto = encodeURIComponent(mensaje);
  const url = `https://wa.me/${tel}?text=${texto}`;

  window.open(url, "_blank");
}
