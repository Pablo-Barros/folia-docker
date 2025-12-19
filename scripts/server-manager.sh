#!/bin/bash

# Folia Experimental Server Management Script
# Usage: ./scripts/server-manager.sh [command] [options]

set -e

# Configuration
COMPOSE_FILE="docker-compose.experimental.yml"
CONTAINER_NAME="folia-1.21.11-experimental"
DATA_DIR="./server-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "Folia Experimental Server Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start           Start the server"
    echo "  stop            Stop the server"
    echo "  restart         Restart the server"
    echo "  status          Show server status"
    echo "  logs            Show server logs (follow mode)"
    echo "  console         Connect to server console"
    echo "  backup          Backup server data"
    echo "  update-config   Update server configuration"
    echo "  install-plugin  Install a plugin jar file"
    echo "  remove-plugin   Remove a plugin"
    echo "  list-plugins    List installed plugins"
    echo "  status-detail   Show detailed server status"
    echo "  backup-world    Backup only world data"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start the server"
    echo "  $0 logs                     # Follow server logs"
    echo "  $0 backup                   # Create backup"
    echo "  $0 install-plugin plugin.jar # Install plugin"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}Error: Docker daemon is not running${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: docker-compose is not installed or not in PATH${NC}"
        exit 1
    fi
}

start_server() {
    echo -e "${BLUE}Starting Folia Experimental Server...${NC}"

    if [ ! -d "$DATA_DIR" ]; then
        echo -e "${YELLOW}Creating data directory: $DATA_DIR${NC}"
        mkdir -p "$DATA_DIR"
    fi

    docker-compose -f "$COMPOSE_FILE" up -d

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Server started successfully!${NC}"
        echo -e "${BLUE}Server IP: $(get_server_ip):25565${NC}"
        echo -e "${BLUE}Console: docker attach $CONTAINER_NAME${NC}"
    else
        echo -e "${RED}❌ Failed to start server${NC}"
        exit 1
    fi
}

stop_server() {
    echo -e "${BLUE}Stopping Folia Experimental Server...${NC}"

    docker-compose -f "$COMPOSE_FILE" down

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Server stopped successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to stop server${NC}"
        exit 1
    fi
}

restart_server() {
    echo -e "${BLUE}Restarting Folia Experimental Server...${NC}"
    stop_server
    sleep 2
    start_server
}

show_status() {
    echo -e "${BLUE}Folia Experimental Server Status:${NC}"
    echo ""

    if docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${GREEN}✅ Server is running${NC}"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

        echo ""
        echo -e "${BLUE}Resource Usage:${NC}"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" "$CONTAINER_NAME"
    else
        echo -e "${RED}❌ Server is not running${NC}"
    fi
}

show_logs() {
    echo -e "${BLUE}Following server logs (Ctrl+C to stop):${NC}"
    docker-compose -f "$COMPOSE_FILE" logs -f
}

connect_console() {
    echo -e "${BLUE}Connecting to server console (Ctrl+P, Ctrl+Q to detach):${NC}"
    docker attach "$CONTAINER_NAME"
}

backup_server() {
    BACKUP_DIR="./backups"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_NAME="folia_backup_$TIMESTAMP"

    echo -e "${BLUE}Creating server backup: $BACKUP_NAME${NC}"

    mkdir -p "$BACKUP_DIR"

    # Create backup excluding logs
    tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
        -C "$DATA_DIR" \
        --exclude='logs/*' \
        --exclude='*.log' \
        --exclude='cache/*' \
        .

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz${NC}"

        # Keep only last 10 backups
        cd "$BACKUP_DIR"
        ls -t *.tar.gz | tail -n +11 | xargs rm -f --
        cd ..
    else
        echo -e "${RED}❌ Backup creation failed${NC}"
        exit 1
    fi
}

backup_world() {
    BACKUP_DIR="./backups/worlds"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    echo -e "${BLUE}Creating world backup: world_backup_$TIMESTAMP${NC}"

    mkdir -p "$BACKUP_DIR"

    if [ -d "$DATA_DIR/world" ]; then
        tar -czf "$BACKUP_DIR/world_backup_$TIMESTAMP.tar.gz" -C "$DATA_DIR" world/
        echo -e "${GREEN}✅ World backup created: world_backup_$TIMESTAMP.tar.gz${NC}"
    else
        echo -e "${YELLOW}⚠️  No world directory found to backup${NC}"
    fi

    if [ -d "$DATA_DIR/world_nether" ]; then
        tar -czf "$BACKUP_DIR/nether_backup_$TIMESTAMP.tar.gz" -C "$DATA_DIR" world_nether/
        echo -e "${GREEN}✅ Nether backup created: nether_backup_$TIMESTAMP.tar.gz${NC}"
    fi

    if [ -d "$DATA_DIR/world_the_end" ]; then
        tar -czf "$BACKUP_DIR/end_backup_$TIMESTAMP.tar.gz" -C "$DATA_DIR" world_the_end/
        echo -e "${GREEN}✅ End backup created: end_backup_$TIMESTAMP.tar.gz${NC}"
    fi
}

install_plugin() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify plugin jar file${NC}"
        echo "Usage: $0 install-plugin plugin.jar"
        exit 1
    fi

    PLUGIN_FILE="$1"
    PLUGIN_NAME=$(basename "$PLUGIN_FILE")

    if [ ! -f "$PLUGIN_FILE" ]; then
        echo -e "${RED}Error: Plugin file not found: $PLUGIN_FILE${NC}"
        exit 1
    fi

    if [[ ! "$PLUGIN_FILE" == *.jar ]]; then
        echo -e "${RED}Error: Plugin file must be a .jar file${NC}"
        exit 1
    fi

    echo -e "${BLUE}Installing plugin: $PLUGIN_NAME${NC}"

    mkdir -p "$DATA_DIR/plugins"
    cp "$PLUGIN_FILE" "$DATA_DIR/plugins/"

    echo -e "${GREEN}✅ Plugin installed: $PLUGIN_NAME${NC}"
    echo -e "${YELLOW}⚠️  Restart server to load the plugin${NC}"
}

remove_plugin() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify plugin name${NC}"
        echo "Usage: $0 remove-plugin plugin.jar"
        exit 1
    fi

    PLUGIN_NAME="$1"
    PLUGIN_PATH="$DATA_DIR/plugins/$PLUGIN_NAME"

    if [ ! -f "$PLUGIN_PATH" ]; then
        echo -e "${RED}Error: Plugin not found: $PLUGIN_NAME${NC}"
        exit 1
    fi

    echo -e "${BLUE}Removing plugin: $PLUGIN_NAME${NC}"
    rm "$PLUGIN_PATH"

    echo -e "${GREEN}✅ Plugin removed: $PLUGIN_NAME${NC}"
    echo -e "${YELLOW}⚠️  Restart server to fully unload the plugin${NC}"
}

list_plugins() {
    echo -e "${BLUE}Installed Plugins:${NC}"
    echo ""

    if [ -d "$DATA_DIR/plugins" ]; then
        if [ "$(ls -A "$DATA_DIR/plugins")" ]; then
            for plugin in "$DATA_DIR/plugins"/*.jar; do
                if [ -f "$plugin" ]; then
                    PLUGIN_SIZE=$(du -h "$plugin" | cut -f1)
                    PLUGIN_MOD=$(stat -c %y "$plugin")
                    PLUGIN_FILE=$(basename "$plugin")
                    echo -e "${GREEN}📦 $PLUGIN_FILE${NC} ($PLUGIN_SIZE, modified: $PLUGIN_MOD)"
                fi
            done
        else
            echo -e "${YELLOW}No plugins installed${NC}"
        fi
    else
        echo -e "${YELLOW}Plugins directory not found${NC}"
    fi
}

show_detailed_status() {
    echo -e "${BLUE}=== Folia Experimental Server Detailed Status ===${NC}"
    echo ""

    # Container status
    echo -e "${BLUE}Container Status:${NC}"
    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Uptime}}\t{{.Ports}}"
    echo ""

    # Resource usage
    echo -e "${BLUE}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" "$CONTAINER_NAME"
    echo ""

    # Disk usage
    if [ -d "$DATA_DIR" ]; then
        echo -e "${BLUE}Disk Usage:${NC}"
        du -sh "$DATA_DIR"/* 2>/dev/null | sort -hr | head -10
        echo ""
    fi

    # Network connectivity
    echo -e "${BLUE}Network Status:${NC}"
    SERVER_IP=$(get_server_ip)
    if nc -z "$SERVER_IP" 25565 2>/dev/null; then
        echo -e "${GREEN}✅ Server is accessible via $SERVER_IP:25565${NC}"
    else
        echo -e "${RED}❌ Server is not accessible via $SERVER_IP:25565${NC}"
    fi
    echo ""

    # Recent logs
    echo -e "${BLUE}Recent Logs (last 10 lines):${NC}"
    docker logs --tail 10 "$CONTAINER_NAME" 2>/dev/null | sed 's/^/  /'
}

get_server_ip() {
    # Try to get the actual IP the server is bound to
    docker port "$CONTAINER_NAME" 25565/tcp 2>/dev/null | cut -d: -f2 | xargs -n1
}

# Main command router
case "$1" in
    start)
        check_docker
        start_server
        ;;
    stop)
        check_docker
        stop_server
        ;;
    restart)
        check_docker
        restart_server
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    console)
        check_docker
        connect_console
        ;;
    backup)
        check_docker
        backup_server
        ;;
    backup-world)
        check_docker
        backup_world
        ;;
    install-plugin)
        check_docker
        install_plugin "$2"
        ;;
    remove-plugin)
        check_docker
        remove_plugin "$2"
        ;;
    list-plugins)
        check_docker
        list_plugins
        ;;
    status-detail)
        check_docker
        show_detailed_status
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac