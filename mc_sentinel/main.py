from flask import Flask, Response

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from mc_sentinel.collector import SentinelCollector


app = Flask(__name__)

REGISTRY.register(SentinelCollector())


@app.route("/")
def hello_world():
    return "<p>Hello World!</p>"


@app.route("/metrics")
def metrics():
    """
    This is the exporter that generate a report based of the latest metrics.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
