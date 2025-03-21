# Hypothesis document

This document reports hypotheses regarding the implementation of [mc-sentinel](../README.md). It is not to be considered factual rather than as a list of assumptions about the Magic Castle infrastructure guiding the development and maintenance of mc-sentinel.

> [!NOTE]
>
> - Magic Castle is referred as `MC`
> - Virtual machines created by a deployment are referred as `instances`

## Monitored components

### Instances

Instances are the virtual machines created by a deployment. They are the main components of the infrastructure and are the first failure point to be monitored.

- instances that are tagged `public`, which indicates that they're accessible through internet
- all instances that have a puppet class `rsyslog::client`, these will forward all their logs to instances with class `rsyslog::server`

### Dependencies

Information on the dependencies that should be tracked. This includes checking for the presence of libraries, services, and other components that are required for the infrastructure to function properly.

- Puppet

### Services

List of services that require monitoring. Each service should be checked for availability and proper functioning.

- FreeIPA
- Fail2ban
- JupyterHub
- Slurm
- ...

## Avenues of Implementation

### Two layers

The software could be split into two sub-tools with different levels of dependencies, therefore decreasing the complexity of the first stage of monitoring happening after provisioning but before any instance configuration through Puppet. A second piece of the program that depends on the architecture being able to install it could monitor the rest of the components.

### Localization of execution

#### Local execution

A software executed on the operator's machine instead of inside the cloud architecture would almost guarantee that it can be launched and operated. One of the downsides would be not having direct access to as much information compared to a tool that is located near the components it's trying to monitor.

#### Execution on instances

The diagnostic tool being executed on an instance depends on the good functioning and even the proper provisioning of such instance. An operator would have little feedback from an instance that fails to be created.

Some way to go around that could be to make all instances accountable for their own diagnosis and able to diagnose others with a simple first-layer tool until the architecture is ready to switch to a second-layer tool.

#### Completely dissociated execution

It is also suggested that the tool could be implemented with an existing and comprehensive software such as [netdata](https://github.com/netdata/netdata), while understanding this might be overkill for our needs and on top of being a commercial solution generated expenses.

### Installation

The installation process highly depends on the localization of the execution environment, but here are general guidelines as to how the install can be done.

#### Cloud-init

MC uses cloud-init to perform immediate configuration once Terraform has completed provisioning. The config file for cloud-init is [puppet.yaml](https://github.com/Scirelgar/magic_castle/blob/59a2ab28199ed8f42443ac50c9d15c2df8924f74/common/configuration/puppet.yaml) and uses the `write_files` field to create files on the spot. While it is a simple way to ensure a file is present after provisioning, it requires to hard code a script which is to be avoided.

A better way to have our program fetched by the architecture is to use the `runcmd` field to clone this repo. This also allows for conditional configuration depending on tags.

> [!WARNING]
> In the event that cloud-init would run in an isolated environment without access to internet, an alternative to using repo cloning should be considered.

### Collection of status

#### Log parsing

The class `rsyslog::server` is associated with the `mgmt` tag and the `rsyslog::client` is present on all instances, which means all logs across all instances are forwarded to `mgmt`. Therefore, if only one instance have to run the tool, launching it on `mgmt` would make the most sense. The tool could then analyze logs in search for status related entries.

#### Service polling

Using CLI commands to poll different services and analyze response.

#### TinyStatus

[TinyStatus](https://github.com/harsxv/tinystatus) can perform checks itself when configured to do so and can generate an HTML file to serve to a web server, providing a visually pleasing dashboard to users.

#### PuppetServer reports

A custom reporting system has recently been implemented to create a report of PuppetServer run, which is a recurring event once a MC is deployed. Although it cannot report on accessibility of visibility of the service by testing a port, this can still provide insightful feedback on the configuration of services.
