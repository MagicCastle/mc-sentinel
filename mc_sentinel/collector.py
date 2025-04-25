import subprocess
from prometheus_client.registry import Collector
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from typing import Union
import os
import requests


class SentinelCollector(Collector):
    def __init__(self):
        super().__init__()

    def _status_add_metric(
        self,
        is_success: bool,
        success_metric: Union[CounterMetricFamily, GaugeMetricFamily],
        fail_metric: Union[CounterMetricFamily, GaugeMetricFamily],
    ):
        """Add opposing metrics based on the success value.

        Args:
            is_success (bool): Indicates if the operation was successful.
            success_metric (Union[CounterMetricFamily, GaugeMetricFamily]): Metric to add if successful.
            fail_metric (Union[CounterMetricFamily, GaugeMetricFamily]): Metric to add if failed.
        """
        if is_success:
            success_metric.add_metric([], 1)
            fail_metric.add_metric([], 0)
        else:
            success_metric.add_metric([], 0)
            fail_metric.add_metric([], 1)

    def collect(self):
        """Collect metrics from the Puppet server.

        Yields:
            Union[CounterMetricFamily, GaugeMetricFamily]: Metrics to be collected.
        """

        def puppet_core_install_directory():
            """Checks if the Puppet core install directory exists.

            Returns:
                CounterMetricFamily: A metric indicating the presence of the Puppet core install directory.
            """

            puppet_core_install_directory = CounterMetricFamily(
                "puppet_core_install_directory",
                "Install directory found on machine",
            )
            if os.path.exists("/opt/puppetlabs/bin/puppet"):
                puppet_core_install_directory.add_metric([], 1)
            else:
                puppet_core_install_directory.add_metric([], 0)
            return puppet_core_install_directory

        def puppetserver_port_poll():
            """Polls the Puppet server's port and check for success.

            Attempts to connect to the Puppet server's port and checks if the connection is successful. It uses the requests library to make a GET request to the Puppet server's status endpoint. If the request is successful (HTTP status code 200), it indicates that the port is open and accessible. Otherwise, it indicates a failure.

            Returns:
                tuple: A tuple containing two CounterMetricFamily objects:
                    - puppetserver_port_poll_success: Counter for successful polls.
                    - puppetserver_port_poll_failure: Counter for failed polls.
            """
            puppetserver_port_poll_success = CounterMetricFamily(
                "puppetserver_port_polls_success",
                "Successful poll on puppetserver's port",
            )
            puppetserver_port_poll_failure = CounterMetricFamily(
                "puppetserver_port_polls_failure",
                "Failed poll on puppetserver's port",
            )
            try:
                puppetserver_response = requests.get(
                    "https://mgmt1:8140/status/v1/simple",
                    verify=False,
                )
                if puppetserver_response.status_code == 200:
                    self._status_add_metric(
                        True,
                        puppetserver_port_poll_success,
                        puppetserver_port_poll_failure,
                    )
                else:
                    self._status_add_metric(
                        False,
                        puppetserver_port_poll_success,
                        puppetserver_port_poll_failure,
                    )
            except requests.exceptions.RequestException:
                self._status_add_metric(
                    False,
                    puppetserver_port_poll_success,
                    puppetserver_port_poll_failure,
                )
            return puppetserver_port_poll_success, puppetserver_port_poll_failure

        def puppet_version():
            """Checks the version of the Puppet agent."""
            puppet_version = CounterMetricFamily(
                "puppet_version",
                "Puppet version",
                labels=["major", "minor", "patch", "version"],
            )
            try:
                version = subprocess.run(
                    ["/opt/puppetlabs/bin/puppet", "agent", "--version"],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                version_parts = version.split(".")
                if len(version_parts) == 3:
                    major, minor, patch = version_parts
                    puppet_version.add_metric([major, minor, patch, version], 1)
                else:
                    puppet_version.add_metric([], 0)
            except Exception as e:
                print(
                    "And error occurred looking for Puppet: " + str(e)
                )  # Shows what was wrong in `systemctl status`
                puppet_version.add_metric([], 0)
            return puppet_version

        yield puppet_core_install_directory()
        yield from puppetserver_port_poll()
        yield puppet_version()
