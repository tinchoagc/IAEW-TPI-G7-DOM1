# app/messaging/event_publisher.py
import aio_pika
import asyncio
import json
from app.config import settings

class EventPublisher:
    def __init__(self):
        self.connection: aio_pika.Connection | None = None
        self.channel: aio_pika.Channel | None = None

    async def connect(self):
        """Se conecta a RabbitMQ y crea un canal."""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            print("Conexión exitosa a RabbitMQ")
        except asyncio.TimeoutError:
            print(f"Error: Timeout al conectar con RabbitMQ en {settings.RABBITMQ_URL}")
        except Exception as e:
            print(f"Error al conectar con RabbitMQ: {e}")

    async def close(self):
        """Cierra la conexión."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        print("Conexión a RabbitMQ cerrada")

    async def publish_message(self, routing_key: str, message: dict):
        """
        Publica un mensaje en el exchange 'default'.
        El routing_key definirá a qué cola va (ej: "reminder.requested").
        """
        if not self.channel:
            print("Error: No hay canal de RabbitMQ para publicar. Conectando...")
            await self.connect() # Intenta reconectar
            if not self.channel:
                print("Error fatal: No se pudo establecer canal con RabbitMQ.")
                return

        # El diagrama menciona "Publica 'ReminderRequested' al broker (RabbitMQ)"
        # Usaremos el exchange por defecto (topic) para simplificar
        exchange = await self.channel.declare_exchange(
            'topic_exchange', 
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=routing_key
        )
        print(f"Mensaje publicado en exchange 'topic_exchange' con routing key '{routing_key}'")

# Creamos una instancia global que la app usará
event_publisher = EventPublisher()