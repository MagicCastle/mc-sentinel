from flask import Flask, Response

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


app = Flask(__name__)

puppet_status_request = Counter(
    "puppet_status_request",
    "Records the number of status request for puppet",
    labelnames=["state"],
)


def get_puppet_version():
    if shutil.which("puppet"):
        puppet_status_request.labels(state="success").inc()
    else:
        puppet_status_request.labels(state="failure").inc()


@app.route("/")
def hello_world():
    return "<p>Hello World!</p>"


@app.route("/metrics")
def metrics():
    """
    This is the exporter that generate a report based of the latest metrics.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/manual-recording")
def man_recording():
    """
    Endpoint to trigger the manual collection of metrics by Collectors.
    """
    get_puppet_version()
    return Response("Manuel recording succeeded")
