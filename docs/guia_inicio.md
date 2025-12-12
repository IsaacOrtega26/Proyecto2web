## Guía de Inicio del Proyecto

# Propósito del Sistema
Este proyecto implementa un sistema automatizado capaz de:

- Extraer información de productos desde un sitio web real (Tienda Monge).
- Almacenar los productos en una base de datos.
- Descargar archivos asociados a cada producto (imágenes).
- Detectar cambios automáticamente, como:
1. productos nuevos,
2. productos eliminados,
3. modificaciones en precios,
4. cambios en archivos,
5. archivos desaparecidos en el origen.
6. Mantener un registro de todo en un archivo de logs.
7. Exponer la información para un frontend a través de una API.
8. Todo el funcionamiento sucede automáticamente, gracias a un scheduler.

# Arquitectura General
El sistema se divide en varios componentes principales:

1. Scrapers
Hay dos scrapers: uno estático y uno dinámico.
- Se encargan de recorrer el sitio web, identificar productos y recolectar datos como nombre, precio, enlace al producto e imagen del artículo.

2. Almacenamiento
Los productos recolectados se guardan en una base de datos PostgreSQL.
Existe un control adicional para los archivos descargados, como imágenes, donde se almacena su hash para detectar cambios.

3. Descarga de Archivos
Cada producto tiene asociada una imagen. El sistema la descarga y la guarda localmente.
Si una imagen cambia en el sitio original, el sistema lo detecta y reemplaza la copia local.

4. Detección de Cambios
El sistema reconoce automáticamente cuando:
- aparece un producto nuevo.
- desaparece uno existente.
- cambia el precio de un producto.
- cambia el archivo asociado.
- un archivo ya no existe en la web.
- Cada evento queda registrado en un log legible para auditoría.

5. API Backend
Una API permite al frontend acceder a los datos procesados de forma sencilla.

6. Scheduler
Es el componente que activa todo el sistema cada cierto tiempo, sin intervención manual.

# Flujo Completo del Sistema
El scheduler inicia los scrapers de manera periódica.
Los scrapers recolectan productos desde la página web.
El sistema compara lo recolectado con lo que ya existe:
- agrega nuevos productos.
- actualiza los que cambiaron.
- elimina los que ya no existen.
- La descarga de archivos obtiene las imágenes y detecta cambios a través de su hash.
- Se registran todos los eventos importantes en un archivo de logs.
- La API expone los datos al frontend.
- El frontend muestra la información al usuario.

# Ejecución del Proyecto
El sistema se ejecuta completamente mediante Docker.
Con un solo comando arranca:
- la aplicación backend.
- la base de datos.
- pgAdmin para administrar la base.
- y el scheduler encargado de la automatización.

El proyecto no requiere configuraciones adicionales una vez iniciado; todo el procesamiento es automático.

# Logs y Auditoría
Todos los cambios quedan documentados en un archivo de registro ubicado dentro del contenedor.
- Incluye eventos como:
- nuevos productos detectados,
- modificaciones en precios,
- archivos nuevos o cambiados,
- productos eliminados,
- archivos eliminados.
- Este log permite verificar el comportamiento del sistema en cualquier momento.

# Frontend y Visualización
- El proyecto incluye una vista sencilla que:
- consulta la API.
- muestra los productos almacenados.
- permite comprobar que el sistema está actualizando la información correctamente.

# Finalidad del Proyecto
Este proyecto demuestra:
1. el uso combinado de scraping con Selenium,
2. gestión de datos persistentes,
3. etección inteligente de cambios,
4. manejo automático de archivos,
5. microservicios orquestados con Docker,
6. documentación de procesos mediante logs.

Es una solución completa que replica el funcionamiento de un sistema profesional de monitoreo de datos.
