# Cómo empezar con WebRTC 💿🤳🏼🔊 | Cap. 1

¡Hola developer 👋🏻! En este repo quiero mostrarte de forma sencilla cómo funciona WebRTC con el ejemplo más básico: negociar una conexión y crear un canal de datos bidireccional como haríamos por ejemplo con WebSockets. El objetivo es que veas de forma clara cuáles son los pasos que se deben dar con el objetivo de que entiendas bien el proceso para luego seguir avanzando en escenarios más "complejos" como enviar audio y vídeo, conectar dos navegadores entre sí, etc. Este repo forma parte de mi vídeo de mi canal de YouTube [Cómo empezar con WebRTC 💿🤳🏼🔊 | Cap. 1](https://youtu.be/cOeZycrQS6s)

[![Cómo empezar con WebRTC](https://github.com/user-attachments/assets/eb109575-84ed-4872-94a1-5a142a432fc6)](https://youtu.be/cOeZycrQS6s)


## ¿Qué es WebRTC? 🌐

WebRTC (Web Real-Time Communication) es una tecnología que permite la comunicación en tiempo real entre navegadores web y aplicaciones móviles. Facilita la transmisión de audio, vídeo y datos directamente entre pares sin necesidad de un servidor intermediario.

## ¿Cómo funciona? 🔄

WebRTC utiliza un proceso de negociación entre dos pares para establecer una conexión directa. Este proceso incluye:
1. **Intercambio de ofertas y respuestas (SDP)**: Los pares intercambian información sobre sus capacidades de medios y red.
2. **Intercambio de candidatos ICE**: Los pares intercambian información sobre las direcciones IP y puertos que pueden utilizar para comunicarse.
3. **Establecimiento de la conexión**: Una vez que ambos pares tienen la información necesaria, pueden establecer una conexión directa y comenzar a intercambiar datos.

## ¿Qué necesitas para empezar? 🛠️

Para ejecutar este proyecto necesitas tener instalado Python 3.9 o superior 🐍.

## Crea un entorno virtual 🛡️

Utiliza un virtual environment para evitar conflictos con otras dependencias de tu sistema.

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate  # En Windows
``` 

### Instala las dependencias 📦

Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Crea certificados SSL 🔒

Cuando trabajamos con WebRTC, es necesario utilizar HTTPS y certificados SSL. Puedes generar certificados autofirmados para propósitos de desarrollo.

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

Para ejecutar el proyecto, utiliza el siguiente comando:

```bash
python app.py
```
