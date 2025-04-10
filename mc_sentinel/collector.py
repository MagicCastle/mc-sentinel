from prometheus_client.registry import Collector, REGISTRY
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
import os
import requests


class SentinelCollector(Collector):
    def __init__(self):
        super().__init__()

    def collect(self):
        """
        This method is called by the Prometheus client to collect metrics.
        """
        # Metrics
        puppet_core_install_directory = CounterMetricFamily(
            "puppet_core_install_directory",
            "Install directory found on machine",
        )
        puppetserver_port_poll_success = CounterMetricFamily(
            "puppetserver_port_polls_success",
            "Successful poll on puppetserver's port",
        )
        puppetserver_port_poll_failure = CounterMetricFamily(
            "puppetserver_port_polls_failure",
            "Failed poll on puppetserver's port",
        )
        dummy_metric = GaugeMetricFamily(
            "dummy_metric",
            "Dummy metric for testing purposes",
        )

        # Add the dummy metric to the collector
        dummy_metric.add_metric([], 1)

        # Collection
        if os.path.exists("/opt/puppetlabs/bin/puppet"):
            puppet_core_install_directory.add_metric([], 1)
        else:
            puppet_core_install_directory.add_metric([], 0)

        # Check if the puppet server is running and accessible
        try:
            puppetserver_status = requests.get(
                "https://mgmt1:8140/status/v1/simple",
                verify=False,
            )
            if puppetserver_status.status_code == 200:
                puppetserver_port_poll_success.add_metric([], 1)
                puppetserver_port_poll_failure.add_metric([], 0)
            if puppetserver_status.status_code == 503:
                puppetserver_port_poll_success.add_metric([], 0)
                puppetserver_port_poll_failure.add_metric([], 1)
        except requests.exceptions.RequestException:
            puppetserver_port_poll_success.add_metric([], 0)
            puppetserver_port_poll_failure.add_metric([], 1)

        yield puppet_core_install_directory
        yield puppetserver_port_poll_success
        yield puppetserver_port_poll_failure
        yield dummy_metric
