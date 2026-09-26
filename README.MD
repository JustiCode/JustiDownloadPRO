# JustiDownloadPRO 2.0.0 — Nueva versión del proyecto

**JustiDownloadPRO** es un programa portable para el sistema operativo Windows desarrollado por **Mauro Ocampo – JustiCode(drmauroocampo271@gmail.com)**, orientado a facilitar la búsqueda, descarga y reproducción de contenido multimedia mediante una interfaz accesible y optimizada para el uso con lectores de pantalla.

El proyecto nace desde una perspectiva de **accesibilidad universal**, combinando automatización, procesamiento multimedia y herramientas pensadas para ofrecer una experiencia sencilla tanto para usuarios de lectores de pantalla como para otros usuarios de Windows.

## 🚀 Características principales

La versión 2.0.0 incorpora una importante evolución del proyecto, con mejoras en reproducción, descargas, gestión de playlists y compatibilidad con diferentes plataformas multimedia.

Entre las principales novedades se incluyen:

* Reproducción multimedia mediante MotorV8.
* Compatibilidad con diferentes reproductores multimedia instalados en Windows.
* Descarga de contenido mediante `yt-dlp`.
* Compatibilidad con YouTube.
* Compatibilidad con SoundCloud.
* Compatibilidad con Bandcamp.
* Compatibilidad con Mixcloud.
* Compatibilidad con Vimeo.
* Compatibilidad con Twitch.
* Compatibilidad con Spotify mediante reproducción con fallback al navegador.
* Gestión de playlists.
* Selección personalizada de elementos de una playlist.
Descarga de los elementos seleccionados de una playlist.
* Apertura automática del contenido descargado.
* Selección de formato de descarga.
* Mejoras de accesibilidad mediante teclado.
* Mensajes y avisos mediante síntesis de voz.
* Optimización de la navegación con lectores de pantalla.
* Arquitectura preparada para incorporar nuevos servicios y reproductores.

---

## 🎵 Compatibilidad con SoundCloud

JustiDownloadPRO_2.0.0 incorpora compatibilidad con **SoundCloud** mediante el sistema de extracción multimedia utilizado por el proyecto.

Esto permite trabajar con contenido compatible de SoundCloud desde la misma interfaz utilizada para otros servicios multimedia.

El soporte de SoundCloud se basa en el extractor correspondiente de `yt-dlp`, que actualmente incluye soporte para pistas, playlists, usuarios, búsquedas y otros tipos de contenido de SoundCloud.

---

## 🎵 Compatibilidad con Spotify

JustiDownloadPRO incorpora compatibilidad con Spotify mediante MotorV8.

Cuando el contenido puede procesarse mediante la ruta de reproducción disponible, MotorV8 intenta iniciar la reproducción correspondiente.

Si esa ruta no puede utilizarse, el sistema utiliza automáticamente el navegador como mecanismo de fallback.

De esta manera, Spotify puede seguir siendo accesible desde JustiDownloadPRO incluso cuando la reproducción externa no sea posible mediante el motor multimedia.

El comportamiento concreto depende del tipo de URL y de las posibilidades disponibles para ese contenido.

## 📋 Playlists personalizadas

Una de las nuevas funciones de JustiDownloadPRO permite seleccionar individualmente qué elementos de una playlist se desean procesar.

El flujo es:

1. Seleccionar una playlist.
2. Abrir **Playlist Personalizada**.
3. Marcar los elementos deseados.
4. Confirmar la selección.
5. JustiDownloadPRO procesa únicamente los elementos seleccionados.

La ventana de selección está diseñada para poder utilizarse mediante teclado y lectores de pantalla.

También dispone de la opción **Cancelar**, permitiendo cerrar la ventana sin iniciar ninguna descarga.

---

## ▶️ Reproducción multimedia

JustiDownloadPRO utiliza **MotorV8** como capa encargada de clasificar las URL y decidir el procedimiento adecuado de reproducción.

El motor puede trabajar con:

* Archivos locales.
* Streams.
* Contenido que requiere extracción.
* Contenido que debe abrirse mediante navegador.

Cuando existe un archivo multimedia local, Windows puede utilizar la aplicación asociada al tipo de archivo.

Para determinadas reproducciones mediante URL, MotorV8 puede utilizar los reproductores multimedia disponibles en el sistema.

Entre los reproductores contemplados por el proyecto se encuentran:

* PotPlayer.
* VLC.
* Sonarpad
* MPC-HC.
* MPC-BE.
* MPV.
* GOM Player.

La arquitectura está preparada para continuar ampliando esta compatibilidad.

---

## 📥 Descargas

Las descargas utilizan `yt-dlp` como motor de extracción multimedia.

El proyecto utiliza además herramientas auxiliares como **FFmpeg** y **Deno** cuando son necesarias para determinados procesos de extracción y procesamiento multimedia.

JustiDownloadPRO genera los archivos temporales en una carpeta propia dentro del directorio temporal de Windows.

---

## 🎚️ Formatos

La interfaz permite seleccionar diferentes formatos de descarga, entre ellos:

* MP3
* MP4
* M4A
* WAV

La selección del formato se realiza desde la interfaz de JustiDownloadPRO.

---

## 🔊 Accesibilidad

JustiDownloadPRO está diseñado teniendo en cuenta el uso cotidiano con lectores de pantalla.

El programa incorpora:

* navegación mediante teclado;
* controles accesibles;
* mensajes mediante síntesis de voz;
* cuadros de diálogo accesibles;
* listas navegables mediante teclado;
* botones accesibles;
* selección mediante teclado;
* confirmaciones y mensajes durante las operaciones principales.

El objetivo es que las funciones principales puedan utilizarse sin depender exclusivamente de una interfaz visual.

---

## 🆕 Mejoras de la versión 2.0.0

### Motor multimedia

* Incorporación y evolución del **MotorV8**.
* Clasificación automática de URL.
* Separación de las rutas de reproducción según el tipo de contenido.
* Compatibilidad con archivos locales, streams, extracción y navegador.
* Preparación para ampliar la compatibilidad con nuevos reproductores.

### Descargas

* Mejor gestión de descargas temporales.
* Integración con FFmpeg.
* Integración con Deno para los procesos compatibles de extracción.
* Mejor gestión de archivos generados.
* Apertura automática del contenido descargado cuando esta opción está habilitada.

### Playlists

* Incorporación de **Playlist Personalizada**.
* Selección individual de elementos.
* Cancelación de la ventana de selección.
* Procesamiento únicamente de los elementos seleccionados.

### Plataformas

* YouTube.
* SoundCloud.
* Bandcamp.
* Mixcloud.
* Vimeo.
* Twitch.
* Facebook
* Instagram
* Spotify.
* Y otras fuentes compatibles con `yt-dlp`.

> La compatibilidad concreta de cada sitio depende del extractor disponible en la versión de `yt-dlp` utilizada, ya que los servicios web pueden cambiar sus interfaces y mecanismos de acceso.

---

## ⚙️ Requisitos

* Windows x64.
* Python 3.x durante el desarrollo.
* `yt-dlp`.
* FFmpeg.
* Deno cuando sea requerido por determinados extractores.
* Uno o más reproductores multimedia compatibles para la reproducción externa.

---

## 🧑‍🦯 Diseñado para accesibilidad

JustiDownloadPRO nace desde una experiencia real de uso con lectores de pantalla.

El proyecto busca facilitar el acceso a herramientas multimedia para:

* personas con discapacidad visual (Total o parcial);
* personas con baja visión;
* usuarios de NVDA;
* usuarios de  Jaws
* usuarios que prefieren trabajar mediante teclado;
* y cualquier persona que valore una interfaz sencilla y accesible.

La accesibilidad no se considera una función adicional, sino una parte troncal del diseño del  programa.

---

## 🛠️ Estado del proyecto

JustiDownloadPRO continúa en desarrollo.

Las futuras versiones podrán incorporar:

* nuevos servicios multimedia;
* nuevos reproductores;
* mejoras de reproducción;
* nuevas herramientas para playlists;
* mejoras de accesibilidad;
* optimizaciones de rendimiento;
* nuevas funciones orientadas a la automatización multimedia.

---

## 👨‍💻 Autor

**Mauro Ocampo – JustiCode**

---

## 📂 Repositorio

**JustiDownloadPRO**

https://github.com/JustiCode/JustiDownloadPRO

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia especificada en el repositorio.

---

## 🙏 Agradecimientos

Gracias a todas las personas y compañeros que prueban JustiDownloadPRO en su ettape de  contrastación "BETA", informan errores, aportan sugerencias y ayudan a mejorar la accesibilidad del proyecto.

Las pruebas realizadas en diferentes equipos, versiones de Windows, reproductores y configuraciones son fundamentales para detectar problemas de compatibilidad y continuar mejorando el motor multimedia.

---

## ⏳Historial de Versiones

**Versión 1.0.0 _ Primera versión pública.

Versión 1.1.0 _ Segunda versión pública

Versión 2.0.0 — Tercera versión pública** 

## 🔥 JustiCode

**Accesibilidad, automatización y software pensado para todos  y todas.**

## 🌐 Contacto y Comunidad
* **YouTube:** [Justicia Ciega](https://www.youtube.com/channel/UCBQ80jeP7QGvjUIsnrMSCng)
* **Blog:** [Justicia Cesgada](https://justiciacesgada.blogspot.com)
* **Email:** justiciaciega45@gmail.com

---
*Hecho en Buenos Aires, Argentina en septiembre de 2026. Porque la tecnología debe ser para todos y todas.*

¡Que no te digan que no podés!
