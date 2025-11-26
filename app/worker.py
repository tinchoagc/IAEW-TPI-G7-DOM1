import asyncio
import json
import aio_pika
import smtplib
from email.message import EmailMessage
from app.config import settings
from app.database import SessionLocal
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.professional import Professional

# --- COMPONENTE 3: MessagingClient ---
class MessagingClient:
    def send_email_smtp(self, destinatario: str, subject: str, body: str):
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = "sistema@turnos.com"
        msg['To'] = destinatario

        try:
            with smtplib.SMTP("mailpit", 1025) as server:
                server.send_message(msg)
            print(f"✅ [MessagingClient] Enviado a {destinatario}")
        except Exception as e:
            print(f"❌ [MessagingClient] Error técnico enviando correo: {e}")

# --- COMPONENTE 2: NotificationService ---
class NotificationService:
    def __init__(self):
        self.messaging_client = MessagingClient()

    def _get_patient_email(self, patient_id: int) -> str:
        db = SessionLocal()
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                return patient.email
            return "unknown@user.com"
        except Exception as e:
            print(f"⚠️ Error DB: {e}")
            return "error@db.com"
        finally:
            db.close()

    def process_notification(self, data: dict):
        print(f"⚙️ [NotificationService] Procesando turno #{data['appointment_id']} - Estado: {data.get('status')}")
        
        patient_id = data['patient_id']
        email_destino = self._get_patient_email(patient_id)
        status = data.get('status', 'PENDING') # Leemos el estado

        # --- LÓGICA DE TEXTOS SEGÚN ESTADO ---
        if status == 'CONFIRMED':
            asunto = f"✅ Turno #{data['appointment_id']} CONFIRMADO"
            cuerpo = (
                f"Hola!\n\n"
                f"Buenas noticias. Tu profesional ha confirmado el turno.\n"
                f"Te esperamos el día: {data['date']}\n\n"
                f"Por favor, asiste con 10 minutos de antelación.\n"
            )
        
        elif status == 'CANCELLED':
            asunto = f"❌ Turno #{data['appointment_id']} CANCELADO"
            cuerpo = (
                f"Hola,\n\n"
                f"Lamentamos informarte que tu turno ha sido cancelado.\n"
                f"Fecha original: {data['date']}\n\n"
                f"Por favor, ingresa al sistema para solicitar uno nuevo.\n"
            )

        else: # PENDING (Por defecto al crear)
            asunto = f"Solicitud de Turno #{data['appointment_id']} Recibida"
            cuerpo = (
                f"Hola!\n\n"
                f"Hemos recibido tu solicitud de reserva.\n"
                f"Estado actual: PENDIENTE DE CONFIRMACIÓN.\n"
                f"Fecha solicitada: {data['date']}\n\n"
                f"Te notificaremos cuando el profesional confirme.\n"
            )
        
        cuerpo += f"\nSaludos,\nConsultorios TurnosApp."

        # Enviamos el mail con el texto elegido
        self.messaging_client.send_email_smtp(email_destino, asunto, cuerpo)

# --- COMPONENTE 1: ReminderConsumer ---
class ReminderConsumer:
    def __init__(self):
        self.notification_service = NotificationService()

    async def consume(self):
        print("🐰 [ReminderConsumer] Conectando a RabbitMQ...")
        # Intentos de conexión con backoff para evitar crash en arranque del stack
        max_retries = 10
        delay = 2
        connection = None
        for attempt in range(1, max_retries + 1):
            try:
                connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                break
            except Exception as e:
                print(f"⚠️ [ReminderConsumer] Fallo conectando a RabbitMQ (intento {attempt}/{max_retries}): {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)

        if connection is None:
            print("❌ [ReminderConsumer] No se pudo conectar a RabbitMQ tras varios intentos. Saliendo.")
            return

        channel = await connection.channel()
        
        exchange = await channel.declare_exchange('topic_exchange', aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue("notifications_queue", durable=True)
        await queue.bind(exchange, routing_key="reminder.requested")

        print("👂 [ReminderConsumer] Esperando mensajes...")
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode()
                    event_data = json.loads(body)
                    
                    print(f"📥 [ReminderConsumer] Evento recibido: {event_data['event']}")
                    
                    await asyncio.to_thread(
                        self.notification_service.process_notification, 
                        event_data['data']
                    )

if __name__ == "__main__":
    consumer = ReminderConsumer()
    try:
        asyncio.run(consumer.consume())
    except KeyboardInterrupt:
        print("👋 [Worker] Apagando...")