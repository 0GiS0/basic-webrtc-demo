import ssl
import asyncio
import datetime
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
                active_connections.discard(peer_connection_id)
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

    console.log(f"📊 Active connections: {len(active_connections)}")
    console.log(f"🆔 Peer connection ID: {peer_connection_id}")

    console.log(f"🔗 New connection established: {peer_connection_id}")
    console.log(f"📄 SDP Offer: {offer_sdp.sdp}")
    # Log the offer SDP to check for ICE candidates
    if 'a=candidate' in offer_sdp.sdp:
        console.log("✅ Offer SDP contains ICE candidates.")
    else:
        console.log("❌ Offer SDP does NOT contain ICE candidates.")

    # Canal para la comunicación bidireccional de datos
    data_channel = peer_connection.createDataChannel("chat")

    # Este evento se dispara cuando se crea un canal de datos
    @peer_connection.on('datachannel')
    def on_data_channel(channel):
        console.log(f"📡 Data channel created: {channel.label}")
        # Se manda el primer mensaje al canal de datos
        channel.send("🎉 ¡Hola desde el servidor! La conexión bidireccional está establecida.")
        
        # Iniciar mensajes automáticos cada 30 segundos
        asyncio.create_task(send_periodic_messages(channel, peer_connection_id))
        console.log(f"⏰ Mensajes automáticos iniciados para {peer_connection_id}")

        # Este evento se dispara cuando se recibe un mensaje en el canal de datos
        @channel.on('message')
        def on_message(message):
            console.log(f"📩 Message received: {message}")
            # Se manda una respuesta al cliente
            channel.send(f"📢 Echo desde servidor: {message}")

        # Este evento se dispara cuando el canal de datos se cierra
        @data_channel.on('close')
        def on_data_channel_close():
            console.log("🔴 Data channel closed")

    # Eventos para manejar el estado de la conexión
    @peer_connection.on('connectionstatechange')
    def on_connection_state_change():
        console.log(f"🔄 Connection state changed: {peer_connection.connectionState}")

    # Este evento se dispara cuando se recibe una pista de medios. Puede ser audio, video, etc.
    @peer_connection.on('track')
    def on_track(track):
        console.log(f"🎵 Track received: {track.kind}")

    # Se establece la descripción remota. Es decir, la oferta SDP que se recibe del cliente.
    await peer_connection.setRemoteDescription(offer_sdp)
    # Se crea una respuesta SDP (SDP Answer) para enviar de vuelta al cliente.
    answer = await peer_connection.createAnswer()
    # Y se establece la descripción local con la respuesta SDP.
    await peer_connection.setLocalDescription(answer)

    console.log(f"📝 SDP Answer: {peer_connection.localDescription.sdp}")
    
    # La respuesta se envía al cliente con la SDP generada
    return web.Response(
            content_type="application/json",
            text=json.dumps({"sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}),
        )

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

app.router.add_static('/static/', os.path.join(ROOT, 'static'), show_index=True)  # Archivos estáticos
app.router.add_get('/', home)
app.router.add_post('/offer', offer)


if __name__ == '__main__':
    web.run_app(app, host='localhost', port=5000, ssl_context=ssl_context)
