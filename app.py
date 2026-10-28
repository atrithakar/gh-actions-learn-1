import time
from flask import Flask, request, jsonify, render_template, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- Prometheus Metrics Definition ---
REQUEST_COUNT = Counter(
    'flask_http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_http_request_duration_seconds',
    'HTTP Request Latency in seconds',
    ['method', 'endpoint']
)

# --- Metrics Middleware ---
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Skip tracking for the /metrics endpoint itself to prevent metric noise
    if request.path == '/metrics':
        return response

    request_latency = time.time() - request.start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(request_latency)

    return response


# --- Core Operation Functions ---
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

# Dispatch table mapping request strings to functions
OPERATIONS = {
    'add': add,
    'subtract': subtract,
    'multiply': multiply,
    'divide': divide
}


# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request payload'}), 400
    
    try:
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Inputs must be valid numbers'}), 400

    operation_name = data.get('operation')
    operation_func = OPERATIONS.get(operation_name)

    if not operation_func:
        return jsonify({'error': 'Unknown or missing operation'}), 400

    try:
        result = operation_func(num1, num2)
    except ValueError as e:
        # Catches the Division by zero exception thrown by divide()
        return jsonify({'error': str(e)}), 400

    # Format to drop trailing .0 on whole numbers
    return jsonify({'result': f"{result:g}"})

# --- Prometheus Metrics Route ---
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)