# Cómo funciona WebRTC 🚀

¡Hola developer 👋🏻! En este repo quiero mostrarte de forma sencilla cómo funciona WebRTC en un escenario donde lo que queremos.

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
