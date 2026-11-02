import logging
import json
import time
import random
from datetime import datetime
from flask import Flask, jsonify, request
from pythonjsonlogger import jsonlogger

app = Flask(__name__)

# Configure JSON logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['app'] = 'logql-practice-app'

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Simulate various log patterns for LogQL practice
API_ENDPOINTS = ['/api/users', '/api/orders', '/api/products', '/api/payment', '/api/auth']
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
USER_IDS = [f'user-{i}' for i in range(1, 21)]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500, 502, 503]

@app.route('/')
def index():
    logger.info('Homepage accessed', extra={
        'endpoint': '/',
        'method': 'GET',
        'status_code': 200
    })
    return jsonify({
        'status': 'healthy',
        'app': 'logql-practice-app',
        'version': '2.0',
        'lab': 'Lab 2 - LogQL Queries'
    })

@app.route('/generate-logs')
def generate_logs():
    """Generate diverse log messages for LogQL practice"""
    count = 0

    # Generate API request logs with varying patterns (50%)
    for _ in range(10):
        endpoint = random.choice(API_ENDPOINTS)
        method = random.choice(HTTP_METHODS)
        status_code = random.choice(STATUS_CODES)
        response_time = random.randint(10, 2000)
        user_id = random.choice(USER_IDS)

        log_level = 'INFO'
        if status_code >= 500:
            log_level = 'ERROR'
        elif status_code >= 400:
            log_level = 'WARNING'

        log_func = getattr(logger, log_level.lower())
        log_func(f'{method} {endpoint} {status_code}', extra={
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time,
            'user_id': user_id,
            'request_id': f'req-{random.randint(10000, 99999)}'
        })
        count += 1

    # Generate database logs (20%)
    for _ in range(4):
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        tables = ['users', 'orders', 'products', 'sessions']
        op = random.choice(operations)
        table = random.choice(tables)
        query_time = random.randint(5, 1500)

        if query_time > 1000:
            logger.warning(f'Slow database query: {op} on {table}', extra={
                'operation': op,
                'table': table,
                'query_time_ms': query_time,
                'database': 'postgres',
                'connection_pool_size': random.randint(5, 20)
            })
        else:
            logger.info(f'Database query: {op} on {table}', extra={
                'operation': op,
                'table': table,
                'query_time_ms': query_time,
                'database': 'postgres'
            })
        count += 1

    # Generate authentication logs (15%)
    for _ in range(3):
        auth_events = ['login_success', 'login_failed', 'logout', 'token_refresh', 'token_expired']
        event = random.choice(auth_events)
        user_id = random.choice(USER_IDS)

        if 'failed' in event or 'expired' in event:
            logger.warning(f'Authentication event: {event}', extra={
                'event': event,
                'user_id': user_id,
                'ip_address': f'192.168.1.{random.randint(1, 255)}',
                'user_agent': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
            })
        else:
            logger.info(f'Authentication event: {event}', extra={
                'event': event,
                'user_id': user_id,
                'ip_address': f'192.168.1.{random.randint(1, 255)}'
            })
        count += 1

    # Generate payment logs (10%)
    for _ in range(2):
        payment_statuses = ['completed', 'pending', 'failed', 'refunded']
        status = random.choice(payment_statuses)
        amount = random.uniform(10.0, 999.99)

        if status == 'failed':
            logger.error('Payment processing failed', extra={
                'payment_status': status,
                'amount': round(amount, 2),
                'currency': 'USD',
                'gateway': random.choice(['stripe', 'paypal', 'square']),
                'error_code': f'PAY_ERR_{random.randint(100, 999)}'
            })
        else:
            logger.info('Payment processed', extra={
                'payment_status': status,
                'amount': round(amount, 2),
                'currency': 'USD',
                'gateway': random.choice(['stripe', 'paypal', 'square'])
            })
        count += 1

    # Generate cache logs (5%)
    for _ in range(1):
        cache_ops = ['hit', 'miss', 'set', 'delete', 'expire']
        op = random.choice(cache_ops)
        logger.info(f'Cache {op}', extra={
            'cache_operation': op,
            'cache_key': f'cache:session:{random.randint(1000, 9999)}',
            'cache_ttl_seconds': random.randint(60, 3600)
        })
        count += 1

    return jsonify({
        'status': 'success',
        'logs_generated': count,
        'message': 'Check Loki for generated logs - practice LogQL queries!'
    })

@app.route('/api/<service>')
def api_service(service):
    """Simulate API endpoints"""
    response_time = random.randint(10, 500)
    status_code = random.choice([200, 200, 200, 201, 400, 500])

    if status_code >= 500:
        logger.error(f'API request failed: /api/{service}', extra={
            'endpoint': f'/api/{service}',
            'method': 'GET',
            'status_code': status_code,
            'response_time_ms': response_time,
            'error': 'Internal server error'
        })
    elif status_code >= 400:
        logger.warning(f'API request with client error: /api/{service}', extra={
            'endpoint': f'/api/{service}',
            'method': 'GET',
            'status_code': status_code,
            'response_time_ms': response_time,
            'error': 'Bad request'
        })
    else:
        logger.info(f'API request: /api/{service}', extra={
            'endpoint': f'/api/{service}',
            'method': 'GET',
            'status_code': status_code,
            'response_time_ms': response_time
        })

    return jsonify({
        'service': service,
        'status': 'processed',
        'response_time_ms': response_time
    }), status_code

@app.route('/health')
def health():
    logger.debug('Health check endpoint called')
    return jsonify({'status': 'UP', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/simulate-incident')
def simulate_incident():
    """Simulate an incident with multiple error logs"""
    logger.error('Database connection pool exhausted', extra={
        'error_code': 'DB_POOL_EXHAUSTED',
        'pool_size': 20,
        'active_connections': 20,
        'waiting_requests': 15
    })

    logger.error('Service timeout connecting to payment gateway', extra={
        'error_code': 'GATEWAY_TIMEOUT',
        'gateway': 'stripe',
        'timeout_ms': 5000
    })

    logger.error('High memory usage detected', extra={
        'error_code': 'HIGH_MEMORY',
        'memory_usage_percent': 95,
        'threshold_percent': 90
    })

    return jsonify({
        'incident': 'simulated',
        'errors_generated': 3,
        'message': 'Check Loki for incident logs'
    }), 500

@app.route('/simulate-slow-requests')
def simulate_slow_requests():
    """Generate logs for slow requests"""
    for i in range(5):
        response_time = random.randint(1000, 5000)
        logger.warning(f'Slow request detected', extra={
            'endpoint': random.choice(API_ENDPOINTS),
            'response_time_ms': response_time,
            'threshold_ms': 1000,
            'request_id': f'req-{random.randint(10000, 99999)}'
        })

    return jsonify({
        'slow_requests_generated': 5,
        'message': 'Practice filtering logs with response_time_ms > 1000'
    })

if __name__ == '__main__':
    logger.info('LogQL Practice Application starting...', extra={
        'port': 5000,
        'environment': 'lab',
        'log_format': 'json',
        'lab_number': 2
    })
    app.run(host='0.0.0.0', port=5000, debug=False)
