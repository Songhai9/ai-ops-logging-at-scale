# Lab 1 Assets - Centralized Logging with Grafana Loki

## Overview

This directory contains all the configuration files, application code, and resources needed for Lab 1. These assets are deployed to `/root/` on the student's lab VM.

## Directory Structure

```
assets/
├── README.md                    # This file
├── loki/
│   └── config.yml              # Loki server configuration
├── alloy/
│   └── config.alloy            # Alloy log collection configuration
├── sample-app/
│   ├── Dockerfile              # Container image definition
│   └── app.py                  # Python Flask application
└── grafana/
    └── provisioning/
        └── datasources/
            └── loki-datasource.yml  # Auto-provision Loki datasource
```

## Asset Deployment Flow

1. **Startup Script** (`startups/startup-script.sh`) runs first
   - Pulls required Docker images
   - Creates necessary directories
   - Sets permissions

2. **Assets** are copied from `assets/` to `/root/` on lab VM
   - File structure is preserved
   - `assets/loki/config.yml` → `/root/loki/config.yml`
   - `assets/sample-app/app.py` → `/root/sample-app/app.py`

3. **Student Actions** during the lab
   - Review and understand configuration files
   - Optionally modify configurations (advanced)
   - Use docker-compose.yml to deploy services

## Files Overview

### loki/config.yml

**Purpose**: Configures Grafana Loki server

**Key Configurations**:
- `auth_enabled: false` - Disables multi-tenancy for lab simplicity
- `http_listen_port: 3100` - API endpoint port
- `storage.filesystem` - Local filesystem storage for lab environment
- `schema_config` - Defines TSDB schema (v13, recommended for new deployments)
- `limits_config` - Resource limits to prevent overload

**Students Learn**:
- Loki configuration structure
- Storage backend options
- Schema evolution
- Resource limit

ing

**Customization Options**:
- Change retention period in `limits_config.reject_old_samples_max_age`
- Adjust ingestion limits in `limits_config.ingestion_rate_mb`
- Modify chunk settings for different workloads

### alloy/config.alloy

**Purpose**: Configures Grafana Alloy log collection agent

**Key Configurations**:
- `discovery.docker` - Discovers running Docker containers
- `loki.source.docker` - Collects container logs
- `loki.process` - Pipeline stages for log processing:
  - Extract Docker labels
  - Parse JSON logs
  - Add custom labels
- `loki.write` - Sends logs to Loki

**Students Learn**:
- HCL configuration syntax (used by Alloy)
- Service discovery patterns
- Log processing pipelines
- Label extraction strategies

**Customization Options**:
- Add custom label extraction rules
- Filter specific containers with `relabel_configs`
- Add additional processing stages (decolorize, multiline, etc.)
- Configure retry logic and backoff

### sample-app/Dockerfile

**Purpose**: Defines container image for sample Flask application

**Base Image**: `python:3.11-slim`

**Key Steps**:
1. Set working directory to `/app`
2. Install Python dependencies (flask, python-json-logger)
3. Copy application code
4. Expose port 5000
5. Run Flask application

**Students Learn**:
- Basic Dockerfile structure
- Python application containerization
- Multi-stage builds concept (not used here but can be introduced)

**Customization Options**:
- Add requirements.txt for dependency management
- Include additional Python packages for log processing
- Add health check instructions
- Optimize image size with multi-stage builds

### sample-app/app.py

**Purpose**: Python Flask web application that generates structured logs

**Key Features**:
1. **JSON Logging**: Uses `python-json-logger` for structured output
2. **Custom Formatter**: Adds timestamp, level, app name to each log
3. **Multiple Log Levels**: Generates INFO, WARNING, ERROR logs
4. **API Endpoints**:
   - `/` - Homepage (generates INFO log)
   - `/generate-logs` - Generates batch of mixed-level logs
   - `/health` - Health check endpoint
   - `/simulate-error` - Generates ERROR log on demand

**Log Format**:
```json
{
  "timestamp": "2024-01-15T10:32:15.123Z",
  "level": "ERROR",
  "name": "root",
  "message": "Failed to connect to database",
  "app": "sample-flask-app",
  "error_code": "DB_CONN_TIMEOUT"
}
```

**Students Learn**:
- Structured logging implementation
- JSON log format
- Python logging best practices
- How to add context to logs

**Customization Options**:
- Add more endpoints for different scenarios
- Include user_id, request_id in logs (demonstrating high cardinality)
- Implement different log formats (logfmt, plain text)
- Add distributed tracing context (trace_id, span_id)

### grafana/provisioning/datasources/loki-datasource.yml

**Purpose**: Auto-provisions Loki as a datasource in Grafana

**Key Configurations**:
- Datasource name: "Loki"
- URL: http://loki:3100 (Docker internal network)
- Access mode: Proxy
- Auto-enable: true

**Students Learn**:
- Grafana provisioning system
- Datasource configuration
- Container networking (service name resolution)

**Customization Options**:
- Add basic auth if Loki requires authentication
- Configure custom HTTP headers
- Set timeout values
- Add derived fields for trace-to-log linking

## Verification Commands

### Verify Assets Are Deployed

```bash
# Check directory structure
ls -R /root/

# Verify configuration files exist
ls -l /root/loki/config.yml
ls -l /root/alloy/config.alloy
ls -l /root/sample-app/app.py
ls -l /root/sample-app/Dockerfile

# Check file permissions
stat /root/loki/config.yml
```

### Verify Configurations Are Valid

```bash
# Validate Loki config (run Loki with --verify-config)
docker run --rm -v /root/loki:/etc/loki grafana/loki:3.0.0 \
  -config.file=/etc/loki/config.yml -verify-config

# Validate Alloy config
docker run --rm -v /root/alloy:/etc/alloy grafana/alloy:latest \
  tools validate /etc/alloy/config.alloy

# Validate Docker Compose file
docker compose -f /root/docker-compose.yml config
```

### Verify Services Are Working

```bash
# Check Loki API
curl http://localhost:3100/ready
curl http://localhost:3100/metrics

# Check Alloy API
curl http://localhost:12345/metrics

# Check sample app
curl http://localhost:5000/
curl http://localhost:5000/health
```

## Troubleshooting Assets

### Issue: Configuration File Not Found

**Symptom**: Docker container fails to start with "config file not found"

**Check**:
```bash
# Verify file exists in expected location
ls -l /root/loki/config.yml

# Check volume mount in docker-compose.yml
cat /root/docker-compose.yml | grep -A 2 "volumes:"
```

**Fix**:
Ensure volume mount paths in docker-compose.yml match actual file locations.

### Issue: Permission Denied

**Symptom**: Container cannot read configuration file

**Check**:
```bash
# Check file permissions
ls -l /root/loki/config.yml

# Check ownership
stat /root/loki/config.yml
```

**Fix**:
```bash
# Make files readable
chmod 644 /root/loki/config.yml
chmod 644 /root/alloy/config.alloy

# Ensure directories are accessible
chmod 755 /root/loki
chmod 755 /root/alloy
```

### Issue: Sample App Build Fails

**Symptom**: `docker compose build sample-app` fails

**Check**:
```bash
# Verify Dockerfile exists
ls -l /root/sample-app/Dockerfile

# Check for syntax errors in Dockerfile
cat /root/sample-app/Dockerfile

# Verify app.py exists
ls -l /root/sample-app/app.py
```

**Fix**:
```bash
# Rebuild with verbose output
docker compose build --no-cache sample-app

# Check Docker build logs
docker compose logs sample-app
```

## Advanced Customization

### Adding More Sample Applications

To add additional applications that generate logs:

1. Create new directory in `assets/`:
```bash
mkdir -p assets/another-app
```

2. Add Dockerfile and application code

3. Add service to docker-compose.yml:
```yaml
another-app:
  build: ./another-app
  container_name: another-app
  networks:
    - aiops-logging
  labels:
    logging: "enabled"
```

4. Alloy will automatically discover and collect logs

### Enabling Loki Authentication

To add basic authentication to Loki:

1. Modify `loki/config.yml`:
```yaml
auth_enabled: true

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

auth:
  type: basic
  basic_auth:
    username: admin
    password: admin123
```

2. Update Alloy configuration to include credentials:
```hcl
loki.write "local_loki" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
    basic_auth {
      username = "admin"
      password = "admin123"
    }
  }
}
```

3. Update Grafana datasource provisioning to include auth.

### Adding Log Parsing for Different Formats

To parse logs in formats other than JSON:

**For logfmt format**:
```hcl
stage.logfmt {
  mapping = {
    level = "",
    message = "",
  }
}
```

**For regex parsing**:
```hcl
stage.regex {
  expression = "^(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}) (?P<level>\\w+) (?P<message>.*)$"
}
```

**For multi-line logs (stack traces)**:
```hcl
stage.multiline {
  firstline     = "^\\d{4}-\\d{2}-\\d{2}"
  max_wait_time = "3s"
  max_lines     = 100
}
```

## Best Practices for Assets

### Configuration Files

1. **Include Comments**: Explain non-obvious settings
2. **Use Sensible Defaults**: Works out-of-the-box for lab environment
3. **Document Required Changes**: If students must modify, make it clear
4. **Validate Before Deployment**: Test all configurations locally

### Application Code

1. **Keep It Simple**: Focus on learning objectives, not production complexity
2. **Add Helpful Logs**: Include log messages that explain what's happening
3. **Handle Errors Gracefully**: Show good error handling practices
4. **Include Documentation**: Code comments explain key concepts

### Docker Images

1. **Use Official Base Images**: python:3.11-slim, grafana/loki:3.0.0
2. **Pin Versions**: Avoid `latest` tag in production scenarios
3. **Pre-pull Images**: Startup script should pull all images
4. **Minimize Layers**: Combine RUN commands where possible

### File Organization

1. **Logical Structure**: Group related files together
2. **Clear Naming**: Use descriptive, consistent file names
3. **README in Each Directory**: Explain directory contents
4. **Version Control**: Track all changes to assets

## Support

For issues with assets:

1. Check this README for troubleshooting steps
2. Verify files are deployed to correct locations
3. Validate configurations with provided commands
4. Check Docker logs for detailed error messages
5. Consult main lab readme.md for additional guidance

---

**Asset Version**: 1.0
**Last Updated**: 2025-01-07
**Maintainer**: AIOps Foundations Team