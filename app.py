import ssl
import asyncio
import datetime
import socket
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from rich.console import Console
from aiohttp import web
import os
import json

# Crea la aplicación web con aiohttp
app = web.Application()
# Configura la consola para imprimir mensajes
console = Console()

ROOT = os.path.dirname(os.path.abspath(__file__))

# Diccionario para almacenar conexiones activas
active_connections = set()

# Función para enviar mensajes periódicos
async def send_periodic_messages(channel, peer_connection_id):
    """Envía mensajes automáticos cada 30 segundos para demostrar comunicación bidireccional"""
    count = 1
    try:
        while True:
            await asyncio.sleep(30)  # Esperar 30 segundos
            
            if channel.readyState == 'open':
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                message = f"🤖 Mensaje automático #{count} desde el servidor - {timestamp}"
                channel.send(message)
                console.log(f"🕐 Mensaje automático enviado a {peer_connection_id}: {message}")
                count += 1
            else:
                console.log(f"🔴 Canal cerrado para {peer_connection_id}, deteniendo mensajes automáticos")
                # Si el canal está cerrado, se elimina al peer de la lista de conexiones activas
                console.log(f"🗑️ Eliminando {peer_connection_id} de conexiones activas")
                active_connections.discard(peer_connection_id)
                console.log(f"📊 Conexiones activas: {len(active_connections)}")
                break
                
    except Exception as e:
        console.log(f"❌ Error enviando mensajes automáticos para {peer_connection_id}: {e}")


async def home(request):
    """Para servir la página HTML principal"""
    return web.FileResponse('static/index.html')


async def offer(request):
    """
    Maneja la señalización WebRTC para establecer una conexión con un cliente.
    Recibe una oferta SDP del cliente, crea un RTCPeerConnection, y devuelve una respuesta SDP.
    """
    
    # Recupera los parametros de la solicitud
    params = await request.json()

    offer_sdp = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type']
    )

    peer_connection = RTCPeerConnection()

    peer_connection_id = f"peer_connection_{id(peer_connection)}"

    active_connections.add(peer_connection_id)

    console.log(f"📊 Conexiones activas: {len(active_connections)}")
    console.log(f"🆔 ID de conexión peer: {peer_connection_id}")

    console.log(f"🔗 Nueva conexión establecida: {peer_connection_id}")
    console.log(f"📄 Oferta SDP:\n{offer_sdp.sdp}")
    
    # Log la oferta SDP para revisar candidatos ICE
    if 'a=candidate' in offer_sdp.sdp:
        console.log("✅ La oferta SDP contiene candidatos ICE.")
    else:
        console.log("❌ La oferta SDP NO contiene candidatos ICE.")

    # Canal para la comunicación bidireccional de datos
    data_channel = peer_connection.createDataChannel("chat")

    # Este evento se dispara cuando se crea un canal de datos
    @peer_connection.on('datachannel')
    def on_data_channel(channel):
        console.log(f"📡 Canal de datos creado: {channel.label}")
        # Se manda el primer mensaje al canal de datos
        channel.send("🎉 ¡Hola desde el servidor! La conexión bidireccional está establecida.")
        channel.send(f"🆔 ID de conexión: {peer_connection_id}")
        
        # Iniciar mensajes automáticos cada 30 segundos
        asyncio.create_task(send_periodic_messages(channel, peer_connection_id))
        console.log(f"⏰ Mensajes automáticos iniciados para {peer_connection_id}")

        # Este evento se dispara cuando se recibe un mensaje en el canal de datos
        @channel.on('message')
        def on_message(message):
            console.log(f"📩 Mensaje recibido: {message}")
            # Se manda una respuesta al cliente
            channel.send(f"📢 Eco desde el servidor: {message}")

        # Este evento se dispara cuando el canal de datos se cierra
        @data_channel.on('close')
        def on_data_channel_close():
            console.log("🔴 Canal de datos cerrado")
            # Se elimina al peer de la lista de conexiones activas
            console.log(f"🗑️ Eliminando {peer_connection_id} de conexiones activas")
            active_connections.discard(peer_connection_id)
            console.log(f"📊 Conexiones activas: {len(active_connections)}")

    # Eventos para manejar el estado de la conexión
    @peer_connection.on('connectionstatechange')
    def on_connection_state_change():
        console.log(f"🔄 Estado de la conexión cambiado: {peer_connection.connectionState}")

    # Este evento se dispara cuando se recibe una pista de medios. Puede ser audio, video, etc.
    @peer_connection.on('track')
    def on_track(track):
        console.log(f"🎵 Pista recibida: {track.kind}")

    # Se establece la descripción remota. Es decir, la oferta SDP que se recibe del cliente.
    await peer_connection.setRemoteDescription(offer_sdp)
    # Se crea una respuesta SDP (SDP Answer) para enviar de vuelta al cliente.
    answer = await peer_connection.createAnswer()
    # Y se establece la descripción local con la respuesta SDP.
    await peer_connection.setLocalDescription(answer)

    console.log(f"📝 Respuesta SDP: {peer_connection.localDescription.sdp}")
    
    # La respuesta se envía al cliente con la SDP generada
    return web.Response(
            content_type="application/json",
            text=json.dumps({"sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}),
        )

# Función para obtener la IP de la red privada
def get_private_ip():
    """Obtiene la IP de la red privada para conexiones desde otros equipos"""
    try:
        # Crear un socket temporal para obtener la IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Conectar a una dirección remota (no necesita estar accesible)
            s.connect(("8.8.8.8", 80))
            private_ip = s.getsockname()[0]
            return private_ip
    except Exception as e:
        console.log(f"❌ Error obteniendo IP privada: {e}")
        return "No disponible"

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

app.router.add_static('/static/', os.path.join(ROOT, 'static'), show_index=True)  # Archivos estáticos
app.router.add_get('/', home)
app.router.add_post('/offer', offer)


if __name__ == '__main__':
    # Obtener la IP de la red privada
    private_ip = get_private_ip()
    port = 8000
    
    console.log("🚀 Iniciando servidor WebRTC...")
    console.log("=" * 60)
    console.log("📡 URLs de acceso:")
    console.log(f"🏠 Local:        https://localhost:{port}")
    console.log(f"🌐 Red privada:  https://{private_ip}:{port}")
    console.log("=" * 60)
    console.log("📝 Nota: Para conectar desde otro equipo, usa la URL de red privada")
    console.log("🔒 Asegúrate de que el certificado SSL sea aceptado en el navegador")
    console.log("🔥 Si tienes problemas de acceso, verifica:")
    console.log("   • Firewall del sistema (puerto 8000 abierto)")
    console.log("   • Ambos dispositivos en la misma red WiFi")
    console.log("   • Acepta el certificado SSL 'inseguro' en el navegador")
    console.log("=" * 60)
    
    web.run_app(app, host='0.0.0.0', port=port, ssl_context=ssl_context)
