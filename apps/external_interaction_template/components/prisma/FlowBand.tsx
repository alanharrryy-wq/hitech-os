const steps = [
  ["Venta", "Registra cada pedido o transacción desde la Tablet con caja integrada."],
  ["Registro", "Marca quién hizo qué, cuánto y cómo quedó cada operación."],
  ["Caja", "Controla movimientos, cierres y variaciones de turno con respaldo."],
  ["Inventario", "Actualiza existencias y detecta faltantes antes de cerrar el día."],
  ["Alerta", "Advierte anomalías, descuadres y eventos que exigen atención."],
  ["Decisión", "Entrega información clara para acciones rápidas y responsables."]
];

export function FlowBand() {
  return (
    <section className="section-tight">
      <div className="dark-band">
        <div className="eyebrow">Flujo operativo</div>
        <h2 className="large-title">Venta, registro, caja, inventario, alerta, decisión.</h2>
        <p className="lead">Un flujo simple para conectar la operación: Tablet vende, la PC gobierna y el móvil supervisa. Cada paso aporta control y visibilidad real.</p>
        <div className="flow">
          {steps.map(([title, body]) => (
            <div className="flow-step" key={title}>
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
