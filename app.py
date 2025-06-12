import ssl
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from rich.console import Console
from aiohttp import web
import asyncio
import os
import json


app = web.Application()
console = Console()

ROOT = os.path.dirname(os.path.abspath(__file__))

# Diccionario para almacenar conexiones activas
active_connections = set()


async def home(request):
    """Serve the main HTML page."""
    return web.FileResponse('static/index.html')


async def offer(request):
    """
    Maneja la señalización WebRTC para establecer una conexión con un cliente.
    Recibe una oferta SDP del cliente, crea un RTCPeerConnection, y devuelve una respuesta SDP.
    Registra estadísticas de conexión y maneja la grabación de medios.
    Si se habilita la grabación, guarda los medios en un archivo con un nombre basado en el ID de conexión.
    También maneja canales de datos y monitorea la calidad del audio y video.
    """
    
    # Recupera los parametros de la solicitud
    params = await request.json()
    
    offer_sdfp = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type']
    )

    peer_connection = RTCPeerConnection()

    peer_connection_id = f"peer_connection_{id(peer_connection)}"

    active_connections.add(peer_connection_id)

    console.log(f"Active connections: {len(active_connections)}")
    console.log(f"Peer connection ID: {peer_connection_id}")

    console.log(f"New connection established: {peer_connection_id}")
    console.log(f"SDP Offer: {offer_sdfp.sdp}")
    # Log the offer SDP to check for ICE candidates
    if 'a=candidate' in offer_sdfp.sdp:
        console.log("Offer SDP contains ICE candidates.")
    else:
        console.log("Offer SDP does NOT contain ICE candidates.")

    # Canal para la comunicación bidireccional de datos
    data_channel = peer_connection.createDataChannel("chat")

    @peer_connection.on('datachannel')
    def on_data_channel(channel):
        console.log(f"Data channel created: {channel.label}")

        @channel.on('message')
        def on_message(message):
            console.log(f"Message received: {message}")

        @data_channel.on('close')
        def on_data_channel_close():
            console.log("Data channel closed")

    @peer_connection.on('connectionstatechange')
    def on_connection_state_change():
        console.log(f"Connection state changed: {peer_connection.connectionState}")

    @peer_connection.on('track')
    def on_track(track):
        console.log(f"Track received: {track.kind}")

   
    await peer_connection.setRemoteDescription(offer_sdfp)
    answer = await peer_connection.createAnswer()
    await peer_connection.setLocalDescription(answer)

    console.log(f"SDP Answer: {peer_connection.localDescription.sdp}")
    
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
