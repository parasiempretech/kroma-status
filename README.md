# Estado de KROMA

Monitor propio, ejecutado por GitHub independientemente de la computadora del equipo y del hosting de KROMA.

- Comprueba únicamente la salud pública de web, agenda y copia de seguridad.
- Programado cada cinco minutos; GitHub puede demorar las ejecuciones. No es un SLA.
- Reintenta tres veces antes de abrir un incidente. Cuando se recupera, comenta y cierra el incidente.
- Las alertas llegan por las notificaciones de este repositorio: seguir **Issues** o **All activity**. El correo depende de las preferencias de notificación de la cuenta.
- No contiene datos de clientes, contraseñas, código privado de la agenda ni acceso a su base.
- Los runners estándar en repositorios públicos son gratuitos según [GitHub](https://docs.github.com/en/actions/concepts/billing-and-usage).
- Actualiza el estado mensualmente para mantener actividad y evitar la suspensión por inactividad del repositorio.

Ver las comprobaciones en **Actions → Estado de KROMA** y los incidentes en **Issues**. Un fallo del propio workflow también requiere revisión.
