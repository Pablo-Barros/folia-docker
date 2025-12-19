# Folia Experimental Server 1.21.11-exp2

Este directorio contiene la configuración para ejecutar un servidor Folia experimental versión 1.21.11 build #2 en un entorno de producción.

## Requisitos Previos

- Docker y Docker Compose instalados
- Al menos 16GB de RAM disponibles
- Espacio en disco para los datos del servidor

## Configuración Rápida

### 1. Iniciar el Servidor

```bash
# Usar docker-compose experimental
docker-compose -f docker-compose.experimental.yml up -d

# O usar el script de gestión
./scripts/server-manager.sh start
```

### 2. Verificar Estado

```bash
# Ver estado básico
./scripts/server-manager.sh status

# Ver estado detallado
./scripts/server-manager.sh status-detail
```

### 3. Acceder a los Archivos del Servidor

Los datos del servidor se montan en el directorio `./server-data/`:

```bash
# Estructura de directorios
server-data/
├── world/              # Mundo principal
├── world_nether/        # Mundo Nether
├── world_the_end/       # Mundo The End
├── plugins/             # Plugins instalados
├── config/              # Configuraciones
├── logs/                # Logs del servidor
├── server.properties    # Configuración principal
├── whitelist.json       # Lista blanca de jugadores
├── ops.json            # Operadores del servidor
└── banned-players.json # Jugadores baneados
```

## Gestión del Servidor

### Script de Gestión

Usa `./scripts/server-manager.sh` para todas las operaciones:

```bash
# Iniciar/Parar/Reiniciar
./scripts/server-manager.sh start
./scripts/server-manager.sh stop
./scripts/server-manager.sh restart

# Logs y consola
./scripts/server-manager.sh logs        # Ver logs en vivo
./scripts/server-manager.sh console     # Conectar a consola

# Plugins
./scripts/server-manager.sh list-plugins
./scripts/server-manager.sh install-plugin plugin.jar
./scripts/server-manager.sh remove-plugin plugin.jar

# Backups
./scripts/server-manager.sh backup          # Backup completo
./scripts/server-manager.sh backup-world    # Solo mundos

# Estado
./scripts/server-manager.sh status         # Estado básico
./scripts/server-manager.sh status-detail  # Estado detallado
```

### Docker Compose Directo

```bash
# Iniciar
docker-compose -f docker-compose.experimental.yml up -d

# Ver logs
docker-compose -f docker-compose.experimental.yml logs -f

# Parar
docker-compose -f docker-compose.experimental.yml down

# Reiniciar
docker-compose -f docker-compose.experimental.yml restart
```

## Configuración de Memoria

El servidor está configurado para usar 16GB de RAM con optimización G1GC:

- **MIN_RAM**: 8GB (mínimo reservado)
- **MAX_RAM**: 16GB (máximo permitido)
- **Java Flags**: Optimizados para Folia y G1GC

Puedes ajustar estos valores en `docker-compose.experimental.yml`:

```yaml
environment:
  - MIN_RAM=4G          # Cambia según necesites
  - MAX_RAM=12G         # Cambia según necesites
```

## Configuración del Servidor

### Archivo server.properties

Edita `./server-data/server.properties` para configurar:

```properties
# Configuración básica
difficulty=normal
gamemode=survival
pvp=true
online-mode=true
motd=Servidor Folia Experimental 1.21.11

# Optimización Folia
view-distance=6
simulation-distance=4

# Configuración de red
server-port=25565
server-ip=
```

### Variables de Entorno

Las variables de entorno importantes en `docker-compose.experimental.yml`:

```yaml
environment:
  - MINECRAFT_EULA=true           # ¡Requerido!
  - ONLINE_MODE=true              # Autenticación de Minecraft
  - TZ=America/Mexico_City      # Zona horaria
  - FOLIA_FLAGS=--nojline       # Flags específicos de Folia
```

## Plugins

### Instalación

1. Coloca los archivos `.jar` de los plugins en `./server-data/plugins/`
2. Reinicia el servidor:
   ```bash
   ./scripts/server-manager.sh restart
   ```

### Plugin Management Script

```bash
# Listar plugins instalados
./scripts/server-manager.sh list-plugins

# Instalar plugin
./scripts/server-manager.sh install-plugin EssentialX.jar

# Remover plugin
./scripts/server-manager.sh remove-plugin EssentialX.jar
```

### Plugins Recomendados para Folia

- **EssentialX**: Comandos esenciales y utilidades
- **WorldEdit**: Edición de mundo
- **LuckPerms**: Sistema de permisos
- **Multiverse-Core**: Múltiples mundos
- **Dynmap**: Mapa web del servidor

## Backups

### Backups Automáticos

```bash
# Backup completo (todos los datos excepto logs)
./scripts/server-manager.sh backup

# Backup de solo mundos
./scripts/server-manager.sh backup-world
```

### Ubicación de Backups

Los backups se guardan en `./backups/`:
- `./backups/folia_backup_YYYYMMDD_HHMMSS.tar.gz` - Backup completo
- `./backups/world_backup_YYYYMMDD_HHMMSS.tar.gz` - Mundo principal
- `./backups/nether_backup_YYYYMMDD_HHMMSS.tar.gz` - Nether
- `./backups/end_backup_YYYYMMDD_HHMMSS.tar.gz` - The End

### Restauración

```bash
# Detener el servidor
./scripts/server-manager.sh stop

# Restaurar backup
tar -xzf ./backups/folia_backup_YYYYMMDD_HHMMSS.tar.gz -C ./server-data

# Reiniciar el servidor
./scripts/server-manager.sh start
```

## Monitoreo

### Logs del Servidor

```bash
# Ver logs en vivo
./scripts/server-manager.sh logs

# Ver logs específicos
docker logs folia-1.21.11-experimental 2>&1 | grep -E "(ERROR|WARN)"
```

### Métricas de Rendimiento

```bash
# Uso de recursos en tiempo real
docker stats folia-1.21.11-experimental

# Estado detallado del servidor
./scripts/server-manager.sh status-detail
```

### Conexión del Servidor

- **IP del Servidor**: (IP del host):25565
- **Consola**: `docker attach folia-1.21.11-experimental`
- **Desconexión**: Ctrl+P, Ctrl+Q

## Problemas Comunes

### Servidor no inicia

1. Verifica que la RAM disponible sea suficiente
2. Revisa los logs con `./scripts/server-manager.sh logs`
3. Asegúrate que `MINECRAFT_EULA=true` esté configurado

### Problemas de Memoria

1. Reduce MAX_RAM si experimentas lag
2. Revisa el uso de recursos con `docker stats`
3. Considera usar menos plugins

### Conexión Rechazada

1. Verifica que el puerto 25565 esté abierto
2. Comprueba `ONLINE_MODE=false` para pruebas locales
3. Revisa la configuración de firewall

## Actualizaciones

### Actualizar la Versión

1. Actualiza la imagen en `docker-compose.experimental.yml`
2. Haz backup antes de actualizar
3. Ejecuta `docker-compose pull` y luego `docker-compose up -d`

### Actualizar Plugins

1. Detén el servidor
2. Reemplaza los archivos `.jar` en `./server-data/plugins/`
3. Reinicia el servidor

## Seguridad

### Consideraciones de Producción

- Mantén los plugins actualizados
- Usa contraseñas seguras
- Configura `ops.json` cuidadosamente
- Mantén backups regulares
- Monitoriza el uso de recursos
- Considera usar un firewall

### Archivos Sensibles

- `ops.json` - Permisos de administrador
- `whitelist.json` - Jugadores permitidos
- `server.properties` - Configuración del servidor
- `banned-players.json` - Jugadores baneados

## Soporte

- **Documentación Folia**: https://docs.papermc.io/folia/
- **Discord Folia**: Comunidad oficial de Folia
- **Issues**: Reportar problemas en el repositorio del proyecto

---

**Nota**: Esta es una versión experimental de Folia. Puede contener bugs o inestabilidad. Use con precaución en producción y mantenga backups regulares.