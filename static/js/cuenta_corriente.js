document.addEventListener('DOMContentLoaded', () => {
  const btnExcel = document.getElementById("btn-exportar-excel");

  if (btnExcel) {
    btnExcel.addEventListener("click", function () {
      const form = document.getElementById("form-exportar");

      // Crear una URL con los parámetros del formulario oculto
      const params = new URLSearchParams(new FormData(form));

      fetch(form.action + "?" + params.toString())
        .then(response => {
          if (!response.ok) throw new Error("Error al generar el Excel");
          return response.blob();
        })
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "movimientos_cuenta_corriente.xlsx";
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        })
        .catch(error => {
          console.error("Error al descargar el archivo:", error);
          alert("No se pudo descargar el archivo Excel.");
        });
    });
  }
});
