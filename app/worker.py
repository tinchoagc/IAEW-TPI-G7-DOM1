import asyncio
import json
import aio_pika
from app.config import settings

async def process_message(message: aio_pika.IncomingMessage):
    """
    Esta función se ejecuta cada vez que llega un mensaje nuevo.
    Aquí iría la lógica de enviar el email real.
    """
    async with message.process():
        body = message.body.decode()
        data = json.loads(body)
        
        print(f"📧 [WORKER] Recibido evento: {data['event']}")
        print(f"   Datos: Turno {data['data']['appointment_id']} para el paciente {data['data']['patient_id']}")
        print("   Simulando envío de correo... ✅ Enviado.")
        print("-" * 20)

async def main():
    print("🐰 [WORKER] Iniciando consumidor de recordatorios...")
    
    # 1. Conectar a RabbitMQ
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    
    # 2. Crear canal y declarar la cola
    channel = await connection.channel()
    
    # Declaramos el exchange (el mismo que usa el publisher)
    exchange = await channel.declare_exchange(
        'topic_exchange', 
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )
    
    # Declaramos la cola específica para notificaciones
    queue = await channel.declare_queue("notifications_queue", durable=True)
    
    # 3. Unir la cola al exchange (Binding)
    # Esto dice: "Mándame todo lo que tenga la etiqueta 'reminder.requested'"
    await queue.bind(exchange, routing_key="reminder.requested")
    
    print("🐰 [WORKER] Esperando mensajes. Presiona CTRL+C para salir.")
    
    # 4. Empezar a consumir
    await queue.consume(process_message)
    
    # Mantener el programa corriendo
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 [WORKER] Apagando worker...")