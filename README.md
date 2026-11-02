# Lab 3 Assets: Correlating Metrics and Logs

## Overview

This directory contains all the configuration files and application code needed for Lab 3: Correlating Metrics and Logs.

## Directory Structure

```
assets/
├── docker-compose.yml          # Orchestrates all services
├── prometheus/
│   └── prometheus.yml          # Prometheus configuration
├── loki/
│   └── config.yml              # Loki configuration
├── alloy/
│   └── config.alloy            # Alloy log collection configuration
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasources.yml # Auto-provisions Prometheus & Loki
├── sample-app/
│   ├── app.py                  # Flask application with metrics and logs
│   ├── Dockerfile              # Container image definition
│   └── requirements.txt        # Python dependencies
└── README.md                   # This file
```

## Services

### Prometheus (Port 9090)
- **Purpose**: Collects and stores metrics
- **Configuration**: `prometheus/prometheus.yml`
- **Scrape Targets**:
  - Prometheus itself
  - Node Exporter (system metrics)
  - Sample App (application metrics)
- **Access**: http://localhost:9090

### Node Exporter (Port 9100)
- **Purpose**: Exports system-level metrics
- **Metrics**: CPU, memory, disk, network
- **Access**: http://localhost:9100/metrics

### Loki (Port 3100)
- **Purpose**: Aggregates and stores logs
- **Configuration**: `loki/config.yml`
- **Storage**: Local filesystem (`/tmp/loki`)
- **Access**: http://localhost:3100

### Grafana Alloy (Port 12345)
- **Purpose**: Collects logs from Docker containers
- **Configuration**: `alloy/config.alloy`
- **Features**:
  - Auto-discovers Docker containers
  - Extracts container names and labels
  - Parses JSON logs
  - Forwards logs to Loki
- **Access**: http://localhost:12345

### Grafana (Port 3000)
- **Purpose**: Unified observability dashboard
- **Credentials**: admin / admin
- **Pre-configured Datasources**:
  - Prometheus (default)
  - Loki
- **Access**: http://localhost:3000

### Sample App (Port 5000)
- **Purpose**: Generates metrics and logs for lab exercises
- **Language**: Python (Flask)
- **Features**:
  - JSON structured logging
  - Prometheus metrics endpoint
  - Multiple log levels (INFO, WARNING, ERROR)
  - Incident simulation endpoints
- **Access**: http://localhost:5000

## Sample App Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check - returns app status |
| `/health` | GET | Detailed health check |
| `/generate-logs` | GET | Generates a variety of log messages |
| `/simulate-error` | GET | Generates a simulated error |
| `/simulate-warning` | GET | Generates a performance warning |
| `/simulate-incident` | GET | Simulates a production incident with burst of errors |
| `/simulate-slow-requests` | GET | Generates slow request logs |
| `/metrics` | GET | Prometheus metrics endpoint |

## Quick Start

### 1. Deploy the Stack

```bash
cd /root
docker compose -f assets/docker-compose.yml up -d
```

### 2. Verify Services

```bash
docker compose ps
```

All services should show status "Up".

### 3. Access Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **Sample App**: http://localhost:5000

### 4. Generate Data

```bash
# Generate sample logs
curl http://localhost:5000/generate-logs

# Simulate an incident
curl http://localhost:5000/simulate-incident
```

### 5. View in Grafana

1. Open Grafana (http://localhost:3000)
2. Navigate to Explore
3. Select Prometheus data source to view metrics
4. Select Loki data source to view logs

## Key Concepts for Lab 3

### Consistent Labeling

Both Prometheus metrics and Loki logs use consistent labels:

**Prometheus Labels:**
```
- job: "sample-app"
- instance: "sample-app:5000"
- service: "sample-app"
- container_name: "sample-app"
```

**Loki Labels:**
```
- container_name: "sample-app"
- source: "docker"
- extracted_level: "INFO|WARNING|ERROR"
- app: "sample-flask"
```

The **container_name** label is common to both, enabling correlation.

### Prometheus Metrics

The sample app exposes these metrics:

```
http_requests_total{method, endpoint, status}
http_request_duration_seconds{method, endpoint}
http_errors_total{endpoint, status}
active_connections
```

### Loki Log Streams

Logs are organized by label sets (streams):

```
{container_name="sample-app", source="docker"}
{container_name="sample-app", source="docker", extracted_level="ERROR"}
{container_name="prometheus", source="docker"}
```

## Data Links Configuration

Example data link URL to navigate from Grafana dashboard to logs:

```
/explore?left={"datasource":"Loki","queries":[{"expr":"{container_name=\"sample-app\"}"}],"range":{"from":"${__from}","to":"${__to}"}}
```

This link:
1. Opens Grafana Explore
2. Selects Loki as data source
3. Pre-fills LogQL query
4. Sets time range from dashboard

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose logs loki
docker compose logs prometheus
docker compose logs grafana

# Restart a specific service
docker compose restart loki
```

### No Metrics in Prometheus

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify sample app metrics endpoint
curl http://localhost:5000/metrics
```

### No Logs in Loki

```bash
# Check Alloy is discovering containers
docker compose logs alloy

# Verify Loki API
curl http://localhost:3100/ready

# Check available labels
curl http://localhost:3100/loki/api/v1/labels
```

### Grafana Data Sources Not Working

1. Open Grafana Settings > Data Sources
2. Test the connection for both Prometheus and Loki
3. If failed, check the URL matches the service name in docker-compose.yml

## Stopping the Lab

```bash
# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

## Additional Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Loki Documentation**: https://grafana.com/docs/loki/
- **Grafana Documentation**: https://grafana.com/docs/grafana/
- **LogQL Query Language**: https://grafana.com/docs/loki/latest/logql/

## Lab Goals

By the end of this lab, you should be able to:

1. ✅ Understand consistent labeling across metrics and logs
2. ✅ Configure data links in Grafana dashboards
3. ✅ Create split-view dashboards with metrics and logs
4. ✅ Navigate from metric spikes to relevant logs in seconds
5. ✅ Investigate incidents using unified observability
6. ✅ Reduce Mean Time to Diagnosis (MTTD) by 10x

Happy correlating! 🔗
