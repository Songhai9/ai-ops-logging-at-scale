# Lab 3 Assets: Correlating Metrics and Logs

## 🎉 Lab Improvements & Fixes

### ✅ Question 7 Data Links - NOW WORKING!

**Previous Issue**: Manual data link configuration was complex and error-prone.

**Fix Applied**: Data links are now **pre-configured at the datasource level**! This means:
- ✅ Automatic "View Logs" links appear when hovering over ANY metric data point
- ✅ No manual configuration required
- ✅ Works across all dashboards automatically
- ✅ Three correlation options available: "View Logs", "View All Logs", and "View Error Logs"

**How to Use**:
1. Open any metrics panel in a dashboard
2. Hover over a data point on the graph
3. See "View Logs" links in the tooltip
4. Click to navigate to Explore with pre-filled LogQL query!

### 📊 Pre-Configured Dashboard

A complete demonstration dashboard is now automatically provisioned:
- **Name**: "Lab 3: Unified Observability - Metrics & Logs"
- **Location**: Dashboards → AIOps Labs folder
- **Features**:
  - HTTP Request Rate with data links
  - HTTP Error Rate (perfect for incident investigation)
  - Response time metrics
  - Real-time logs panel (time-synchronized with metrics)
  - Ready for Questions 7-12 validation

### 📚 New Documentation

- **LAB_FIXES_AND_VALIDATION_GUIDE.md** - Comprehensive guide for Questions 7-12 validation
- **QUICK_REFERENCE.md** - Quick reference card with commands and tips

---

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
│       ├── datasources/
│       │   └── datasources.yml # Auto-provisions Prometheus & Loki (with data links!)
│       └── dashboards/
│           ├── dashboards.yml  # Dashboard provisioning config
│           └── unified-observability-dashboard.json # Pre-configured demo dashboard
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

## Data Links Configuration ✅ PRE-CONFIGURED!

Data links are now configured at the **Prometheus datasource level**, meaning they automatically work on all panels without manual configuration!

**Three pre-configured data links**:

1. **"View Logs"** - Shows all logs from sample-app for the selected time range
2. **"View All Logs for Time Range"** - Alternative general logs view
3. **"View Error Logs"** - Filters to show only ERROR level logs (perfect for incident investigation!)

**Configuration Location**: `grafana/provisioning/datasources/datasources.yml`

**How They Work**:
- When you hover over any data point in a Prometheus-based panel
- A tooltip appears with clickable links
- Clicking opens Grafana Explore with:
  - Loki selected as data source
  - Pre-filled LogQL query for sample-app
  - Time range automatically set from `${__from}` to `${__to}` (dashboard time)

**Example URL Structure** (URL-encoded):
```
/explore?left=%7B%22datasource%22:%22Loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bcontainer_name%3D%5C%22sample-app%5C%22%7D%22,%22queryType%22:%22range%22%7D%5D,%22range%22:%7B%22from%22:%22${__from}%22,%22to%22:%22${__to}%22%7D%7D
```

**Testing Data Links**:
```bash
# 1. Generate some traffic
curl http://localhost:5000/generate-logs
curl http://localhost:5000/simulate-incident

# 2. Open Grafana dashboard
# 3. Hover over any data point
# 4. Click "View Logs" or "View Error Logs"
# 5. Verify Explore opens with correct query and time range
```

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
