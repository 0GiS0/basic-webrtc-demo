// Variables globales para almacenar el canal de datos y la conexión peer
var peerConnection = null;
var remoteDataChannel = null;


// Función de log para pintar en consola los mensajes bonitos ✨
function log(message, object) {
    const logElement = document.getElementById("log");
    const timestamp = new Date().toLocaleTimeString();
    
    let objectHtml = '';
    if (object) {
        if (typeof object === 'string') {
            objectHtml = `<span class="log-string">"${object}"</span>`;
        } else if (typeof object === 'object') {
            objectHtml = `<pre class="log-object">${JSON.stringify(object, null, 2)}</pre>`;
        } else {
            objectHtml = `<span class="log-value">${object}</span>`;
        }
    }
    
    logElement.innerHTML += `
        <div class="log-entry">
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
            ${objectHtml}
        </div>
    `;
    
    // Auto-scroll al final
    logElement.scrollTop = logElement.scrollHeight;
    
    console.log(message, object);
}


// Función para enviar mensajes a través del canal de datos
function sendMessage(message) {
    const channel = dataChannel || remoteDataChannel;
    const sendButton = document.getElementById("send");

    if (channel && channel.readyState === 'open' && !sendButton.disabled) {
        channel.send(message);
        log("Mensaje enviado:", message);
    } else {
        log("El canal de datos no está abierto o el botón está deshabilitado");
    }
}

// Mandar el mensaje que se escribe en el input con id "message" cuando se pulsa el botón con id "send"
document.getElementById("send").addEventListener("click", () => {
    const messageInput = document.getElementById("message");
    const message = messageInput.value;
    messageInput.value = ""; // Limpiar el input después de enviar el mensaje
    sendMessage(message);
});

// Mandar el mensaje que se escribe en el input con id "message" cuando se pulsa la tecla Enter
document.getElementById("message").addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        const messageInput = document.getElementById("message");
        const message = messageInput.value;
        sendMessage(message);
        messageInput.value = ""; // Limpiar el input después de enviar el mensaje
    }
});

async function createPeerConnection() {
    //1. Crear la conexión RTCPeerConnection y el canal de datos
    log("1. Iniciando conexión WebRTC 🚀");

    peerConnection = new RTCPeerConnection({
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" }
        ]
    });

    dataChannel = peerConnection.createDataChannel("chat");

    //2. Configurar el evento onopen del canal de datos
    dataChannel.onopen = () => {
        log("Canal de datos abierto");
        // Habilitar el botón de envío cuando el canal esté abierto
        document.getElementById("send").disabled = false;
    };

    //3. Configurar el evento onmessage del canal de datos
    dataChannel.onmessage = (event) => {
        const message = event.data;
        log("Mensaje recibido:", message);
    };

    //4. Configurar el evento onclose del canal de datos
    dataChannel.onclose = () => {
        log("Canal de datos cerrado");
        // Deshabilitar el botón de envío cuando el canal se cierre
        document.getElementById("send").disabled = true;
    };

    //5. Configurar el evento oniceconnectionstatechange para manejar los cambios en el estado de conexión ICE
    peerConnection.oniceconnectionstatechange = (event) => {
        log("Estado ICE:", peerConnection.iceConnectionState);

    };

    //6. Configurar el evento ondatachannel para recibir mensajes del otro extremo
    remoteDataChannel = null;
    peerConnection.ondatachannel = (event) => {

        log("Canal de datos recibido del otro extremo");
        remoteDataChannel = event.channel;

        remoteDataChannel.onmessage = (event) => {
            log("Mensaje recibido en el canal de datos:", event.data);
        };
    };
}

//7. Negociar la conexión WebRTC con el servidor
async function negotiate() {


    try {
        log("2. Se creará una oferta para iniciar la conexión WebRTC 🤝");
        const offer = await peerConnection.createOffer();
        log("Oferta creada 📝:", offer);
        await peerConnection.setLocalDescription(offer);

        // Promesa que espera a que los ICE candidates sean recolectados
        await new Promise((resolve) => {
            peerConnection.onicecandidate = (event) => {
                if (event.candidate === null) {
                    log("Todos los ICE candidates han sido recolectados ✅");
                    resolve();
                } else {
                    log("Nuevo ICE candidate 🥇:", event.candidate);
                }
            };
        });

        //Enviar la oferta al servidor para hacer la conexión
        const response = await fetch("/offer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sdp: peerConnection.localDescription.sdp, type: peerConnection.localDescription.type })
        });

        log("Oferta enviada al servidor, esperando respuesta... ⏳📡");
        const answer = await response.json();
        log("Respuesta recibida del servidor 📬:", answer);
        log("Configurando la descripción remota con la respuesta del servidor 📜");
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));

        log("Conexión WebRTC negociada con éxito 🎉");


    } catch (error) {
        log("Error al negociar la conexión WebRTC 😢:", error);
    }
}

// Esta función se ejecuta cuando se hace clic en el botón "Iniciar conexión"
async function start() {
    await createPeerConnection();
    await negotiate();
}