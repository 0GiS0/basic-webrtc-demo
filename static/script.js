var peerConnection = null;
var remoteDataChannel = null;

// Función para enviar mensajes a través del canal de datos
function sendMessage(message) {
    const channel = dataChannel || remoteDataChannel;

    if (channel && channel.readyState === 'open') {
        channel.send(message);
        console.log("Mensaje enviado:", message);
    } else {
        console.error("El canal de datos no está abierto");
    }
}

// Mandar el mensaje que se escribe en el input con id "message" cuando se presiona Enter
//o se pulsa el botón con id "send"
document.getElementById("send").addEventListener("click", () => {
    const messageInput = document.getElementById("message");
    const message = messageInput.value;
    sendMessage(message);
});

async function createPeerConnection() {
    //1. Crear la conexión RTCPeerConnection y el canal de datos
    console.log("Iniciando conexión WebRTC...");

    peerConnection = new RTCPeerConnection({
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" }
        ]
    });

    dataChannel = peerConnection.createDataChannel("chat");

    //2. Configurar el evento onopen del canal de datos
    dataChannel.onopen = () => {
        console.log("Canal de datos abierto");
    };

    //3. Configurar el evento onmessage del canal de datos
    dataChannel.onmessage = (event) => {
        const message = event.data;
        console.log("Mensaje recibido:", message);
    };

    //4. Configurar el evento onclose del canal de datos
    dataChannel.onclose = () => {
        console.log("Canal de datos cerrado");
    };

    //5. Configurar el evento oniceconnectionstatechange para manejar los cambios en el estado de conexión ICE
    peerConnection.oniceconnectionstatechange = (event) => {
        console.log("Estado ICE:", peerConnection.iceConnectionState);

    };

    //6. Configurar el evento ondatachannel para recibir mensajes del otro extremo
    remoteDataChannel = null;
    peerConnection.ondatachannel = (event) => {

        console.log("Canal de datos recibido del otro extremo");
        remoteDataChannel = event.channel;

        remoteDataChannel.onmessage = (event) => {
            console.log("Mensaje recibido en el canal de datos:", event.data);
        };
    };
}

//7. Negociar la conexión WebRTC con el servidor
async function negotiate() {


    try {
        console.log("Se creará una oferta para iniciar la conexión WebRTC");
        const offer = await peerConnection.createOffer();
        console.log("Oferta creada:", offer);
        await peerConnection.setLocalDescription(offer);

        // // Promesa que espera a que los ICE candidates sean recolectados
        // await new Promise((resolve) => {
        //     peerConnection.onicecandidate = (event) => {
        //         if (event.candidate === null) {
        //             console.log("Todos los ICE candidates han sido recolectados");
        //             resolve();
        //         } else {
        //             console.log("Nuevo ICE candidate:", event.candidate);
        //         }
        //     };
        // });

        //Enviar la oferta al servidor para hacer la conexión
        const response = await fetch("/offer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sdp: peerConnection.localDescription.sdp, type: peerConnection.localDescription.type })
        });

        console.log("Oferta enviada al servidor, esperando respuesta...");
        const answer = await response.json();
        console.log("Respuesta recibida del servidor:", answer);
        console.log("Configurando la descripción remota con la respuesta del servidor");
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));

        console.log("Conexión WebRTC negociada con éxito");


    } catch (error) {
        console.error("Error al negociar la conexión WebRTC:", error);
    }
}


async function start() {
    await createPeerConnection();
    await negotiate();
}