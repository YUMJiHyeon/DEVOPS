# DevOps, Software Evolution and Software Maintenance 
## Cousre code: KSDSESM1KU

### Exam assignment by:

Erle Sognnæs:
s25128@itu.dk

Jihyeon Yum:
s25126@itu.dk

Margrét Edda Friðgeirsdóttir:
s25117@itu.dk

Mathias Anakin Alm:
matal@itu.dk


This report details the design, evolution, and operation of the ITU-MiniTwit system for the 'DevOps, Software Evolution, and Software Maintenance' course. Our group aimed to transform the legacy application into a robust, scalable service by applying modern DevOps principles.

We implemented Infrastructure as Code (IaC) using Vagrant to ensure reproducible environments. To achieve high availability, we deployed an Nginx load balancer integrated with Keepalived, creating an automated failover mechanism. Furthermore, we established comprehensive observability by integrating Prometheus and Grafana for system monitoring and log aggregation. The entire development lifecycle is managed through a CI/CD pipeline, which automates testing and deployment processes.


# Video
**a) Monitoring Dashboards in Action**
![Monotoring dashboard](img/monotoring.gif "monotoring dashboard")
**b) Logging Dashboards in Action**
![Logging dashboard](img/logging.gif "logging dashboard")
**c) IaC in Action**
![IaC in Action](img/IaC5.gif "IaC in Action")	
**d) CI/CD in Action**
![CI/CD pipeline gif](img/CiCdPl.gif "CI/CD pipeline gif")
