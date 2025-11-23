# app/integration/webhook_client.py
import httpx
from app.schemas import Appointment

class WebhookClient:
    def __init__(self):
        # En la vida real, esta URL vendría de la DB (configurada por el usuario)
        # Para el TP, usaremos una variable o un servicio de prueba.
        pass

    async def send_notification(self, url: str, event_name: str, appointment: Appointment):
        """
        Envía una notificación POST a un sistema externo.
        """
        payload = {
            "event": event_name, # Ej: "appointment.confirmed"
            "appointment_id": appointment.id,
            "status": appointment.status,
            "timestamp": str(appointment.updated_at)
        }
        
        print(f"🎣 [WEBHOOK] Intentando notificar a {url}...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Enviamos el POST y esperamos máx 5 segundos
                response = await client.post(url, json=payload, timeout=5.0)
                print(f"🎣 [WEBHOOK] Respuesta: {response.status_code}")
                return response.status_code == 200
            except Exception as e:
                print(f"🎣 [WEBHOOK] Falló el envío: {e}")
                return False