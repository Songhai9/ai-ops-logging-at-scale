import logging
import os
import json
import time
import random
from datetime import datetime
from flask import Flask, jsonify
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Configure JSON logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['app'] = os.getenv('APP_NAME', 'sample-flask-app')
        log_record['container_name'] = os.getenv('CONTAINER_NAME', 'sample-app')

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Prometheus Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['endpoint', 'status']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Simulate various log levels
LOG_MESSAGES = {
    'INFO': [
        'User logged in successfully',
        'API request processed',
        'Cache hit for key: session_{}',
        'Database query completed in {}ms',
        'Request routed to backend service',
        'Authentication token validated',
    ],
    'WARNING': [
        'API rate limit approaching for user_id: {}',
        'Database connection pool at 80% capacity',
        'Slow query detected: {}ms',
        'Memory usage above 75% threshold',
        'Retry attempt {} for failed operation',
    ],
    'ERROR': [
        'Failed to connect to database: connection timeout',
        'API authentication failed for token: invalid_token_{}',
        'Unexpected error in payment processing: {}',
        'Service dependency unavailable: external-api',
        'Data validation failed for request',
        'Failed to write to cache: Redis connection error',
        'Database connection pool exhausted',
    ]
}

@app.route('/')
def index():
    start_time = time.time()
    logger.info('Homepage accessed')
    http_requests_total.labels(method='GET', endpoint='/', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/').observe(time.time() - start_time)
    return jsonify({'status': 'healthy', 'app': 'sample-flask-app', 'version': '1.0'})

@app.route('/generate-logs')
def generate_logs():
    """Generate a variety of log messages"""
    start_time = time.time()
    count = 0

    # Generate INFO logs (70%)
    for _ in range(7):
        msg = random.choice(LOG_MESSAGES['INFO'])
        if '{}' in msg:
            msg = msg.format(random.randint(1, 1000))
        logger.info(msg, extra={'request_id': f'req-{random.randint(1000, 9999)}'})
        count += 1

    # Generate WARNING logs (20%)
    for _ in range(2):
        msg = random.choice(LOG_MESSAGES['WARNING'])
        if '{}' in msg:
            msg = msg.format(random.randint(100, 500))
        logger.warning(msg, extra={'request_id': f'req-{random.randint(1000, 9999)}'})
        count += 1

    # Generate ERROR logs (10%)
    for _ in range(1):
        msg = random.choice(LOG_MESSAGES['ERROR'])
        if '{}' in msg:
            msg = msg.format(random.randint(1, 100))
        logger.error(msg, extra={'request_id': f'req-{random.randint(1000, 9999)}'})
        count += 1

    http_requests_total.labels(method='GET', endpoint='/generate-logs', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/generate-logs').observe(time.time() - start_time)

    return jsonify({
        'status': 'success',
        'logs_generated': count,
        'message': 'Check Loki for generated logs'
    })

@app.route('/health')
def health():
    start_time = time.time()
    logger.debug('Health check endpoint called')
    http_requests_total.labels(method='GET', endpoint='/health', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/health').observe(time.time() - start_time)
    return jsonify({'status': 'UP', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/simulate-error')
def simulate_error():
    start_time = time.time()
    logger.error('Simulated error occurred', extra={
        'error_code': 'SIM_ERROR_500',
        'user_action': 'checkout',
        'trace_id': f'trace-{random.randint(10000, 99999)}',
        'request_id': f'req-{random.randint(1000, 9999)}'
    })
    http_requests_total.labels(method='GET', endpoint='/simulate-error', status='500').inc()
    http_errors_total.labels(endpoint='/simulate-error', status='500').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/simulate-error').observe(time.time() - start_time)
    return jsonify({'error': 'Simulated error', 'code': 'SIM_ERROR_500'}), 500

@app.route('/simulate-warning')
def simulate_warning():
    start_time = time.time()
    logger.warning('Performance degradation detected', extra={
        'response_time_ms': random.randint(1000, 5000),
        'threshold_ms': 1000,
        'service': 'database',
        'request_id': f'req-{random.randint(1000, 9999)}'
    })
    http_requests_total.labels(method='GET', endpoint='/simulate-warning', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/simulate-warning').observe(time.time() - start_time)
    return jsonify({'warning': 'Performance degradation detected', 'check_logs': True})

@app.route('/simulate-incident')
def simulate_incident():
    """Simulate a production incident with burst of errors"""
    start_time = time.time()

    # Generate a burst of errors to simulate an incident
    logger.error('INCIDENT: Database connection pool exhausted', extra={
        'error_code': 'DB_POOL_EXHAUSTED',
        'pool_size': 100,
        'active_connections': 100,
        'waiting_connections': 50,
        'trace_id': f'trace-{random.randint(10000, 99999)}',
        'request_id': f'req-{random.randint(1000, 9999)}'
    })

    # Generate multiple error logs
    for i in range(15):
        logger.error(f'Failed to acquire database connection: timeout after 30s (attempt {i+1})', extra={
            'error_code': 'DB_CONNECTION_TIMEOUT',
            'timeout_ms': 30000,
            'service': 'payment-service',
            'trace_id': f'trace-{random.randint(10000, 99999)}',
            'request_id': f'req-{random.randint(1000, 9999)}'
        })
        http_errors_total.labels(endpoint='/payment', status='500').inc()

    logger.error('INCIDENT: Payment processing failing due to database unavailability', extra={
        'error_code': 'PAYMENT_PROCESSING_FAILED',
        'failed_transactions': 15,
        'trace_id': f'trace-{random.randint(10000, 99999)}',
        'request_id': f'req-{random.randint(1000, 9999)}'
    })

    http_requests_total.labels(method='GET', endpoint='/simulate-incident', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/simulate-incident').observe(time.time() - start_time)

    return jsonify({
        'status': 'incident_simulated',
        'incident_type': 'database_connection_pool_exhausted',
        'errors_generated': 17,
        'message': 'Check your unified observability dashboard to investigate!'
    })

@app.route('/simulate-slow-requests')
def simulate_slow_requests():
    """Simulate slow requests for response time analysis"""
    start_time = time.time()

    # Simulate slow processing
    for i in range(5):
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        logger.warning(f'Slow request detected: {int(delay * 1000)}ms', extra={
            'response_time_ms': int(delay * 1000),
            'threshold_ms': 1000,
            'endpoint': '/api/process',
            'request_id': f'req-{random.randint(1000, 9999)}'
        })
        http_request_duration_seconds.labels(method='POST', endpoint='/api/process').observe(delay)

    http_requests_total.labels(method='GET', endpoint='/simulate-slow-requests', status='200').inc()
    http_request_duration_seconds.labels(method='GET', endpoint='/simulate-slow-requests').observe(time.time() - start_time)

    return jsonify({
        'status': 'success',
        'slow_requests_generated': 5,
        'message': 'Check Prometheus for response time metrics and Loki for slow request logs'
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/webhook/<receiver>', methods=['POST'])
@app.route('/webhook/<category>/<receiver>', methods=['POST'])
def webhook(receiver=None, category=None):
    """Receive webhook notifications from Alertmanager"""
    from flask import request
    start_time = time.time()

    try:
        data = request.get_json()
        receiver_name = f"{category}/{receiver}" if category else receiver

        logger.info(
            f'Webhook received from Alertmanager',
            extra={
                'receiver': receiver_name,
                'status': data.get('status'),
                'alerts_count': len(data.get('alerts', [])),
                'group_labels': data.get('groupLabels', {}),
            }
        )

        for alert in data.get('alerts', []):
            logger.info(
                f"Alert: {alert.get('labels', {}).get('alertname')} - {alert.get('status')}",
                extra={
                    'alertname': alert.get('labels', {}).get('alertname'),
                    'severity': alert.get('labels', {}).get('severity'),
                    'status': alert.get('status'),
                    'summary': alert.get('annotations', {}).get('summary'),
                }
            )

        http_requests_total.labels(method='POST', endpoint='/webhook', status='200').inc()
        http_request_duration_seconds.labels(method='POST', endpoint='/webhook').observe(time.time() - start_time)

        return jsonify({'status': 'received', 'receiver': receiver_name, 'alerts_count': len(data.get('alerts', []))}), 200

    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}')
        http_errors_total.labels(endpoint='/webhook', status='500').inc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info('Sample Flask application starting...', extra={
        'port': 5000,
        'environment': 'lab',
        'log_format': 'json'
    })
    app.run(host='0.0.0.0', port=5000, debug=False)
