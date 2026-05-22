# DevOps, Software Evolution and Software Maintenance
## Cousre code: KSDSESM1KU

### Exam assignment by: GROUP O

Erle Sognnæs:
s25128@itu.dk

Jihyeon Yum:
s25126@itu.dk

Margrét Edda Friðgeirsdóttir:
s25117@itu.dk

Mathias Anakin Alm:
matal@itu.dk


## Overview 

This project details the design, evolution, and operation of the ITU-MiniTwit system for the 'DevOps, Software Evolution, and Software Maintenance' course. Our group aimed to transform the legacy application into a robust, scalable service by applying modern DevOps principles. The major features of our system are as follows:


### a) Twitter immitation
Minitwit.py is a program immitating the most basic of twitters features. Accounts, messages, public and personal timelines, and following users.

### b) Monitoring Dashboards
![Monitoring dashboard](img/monotoring.gif "monotoring dashboard")
This video shows our monitoring dashboard on Grafana in action, visualizing real-application metrics and health collectied via Prometheus as system processes traffic from the simulator.

### c) Logging Dashboards
![Logging dashboard](img/logging.gif "logging dashboard")
This video shows our logging dashboard on Grafana in action, utilizing Loki to aggregate and display real-time event logs as the system processes traffic from the simulator. 

### d) Infrastructure as Code (Iac) 
![IaC in Action](img/IaC5.gif "IaC in Action")	
This video shows the automated creation of three servers using Vagrant and the DigitalOcean provider. The shell provisiong scripts installing essential softwares. It also shows the Minitwit application being deployed and executed via Docker on both the primary and secondary servers.

### e) Automated CI/CD pipeline
![CI/CD pipeline gif](img/CiCdPl.gif "CI/CD pipeline gif")
This video shows our CI/CD pipeline using GitHub Actions. Once merged into the main branch, the pipeline automatically connects to our production droplets via SSH to deploy the changes by restarting the Docker containers with the updated image.

## Deployment
### Live System
The application is currently hosted at [https://devopsgroupo.me](https://devopsgroupo.me).

We utilize Certbot for secure HTTPS communication, but perform configuration manually post-deployment to avoid 'Let's Encrypt' rate limits during frequent automated provisioning.

### Infrastructure
We use DigitalOcean for the VPS droplet. Domain management and DNS resolution are handled through DigitalOcean. To ensure high availability, we use Keepalived and Nginx to manage a Virtual IP (VIP: 129.212.212.105) for automated failover between the primary and secondary nodes. A distributed MongoDB instance running on a dedicated database server. 

Our infrastructure is managed as code using Vagrant. If you want to use a different configuration or scaling startegy, you can customize it by modifying the Vagrantfile.

## Installation
### a) Prerequisties

    Vagrant & DigitalOcean Provider plugin 
    DigitalOcean API Token
    SSH Private Key
    Pre-created Reserved IP
    
### b) Repository Cloning

```bash
git clone https://github.com/YUMJiHyeon/DEVOPS
cd DEVOPS
```

### c) Configuration of Environment Variables
For security reasons, sensitive credentials are managed via an '.env' file, which must be created in the root directory of the project. 


Example `.env` content:

      ```env
      MONGO_URI=mongodb://your_user_for_the_MongoDB_database:your_password@your_db_ip:27017/minitwit?authSource=admin
      SECRET_KEY=A_Secure_key_used_by_Flask_for_session_management_and_appllication_security
      DIGITAL_OCEAN_TOKEN=your_digital_ocean_api_token

## Usage
To deploy the entire distributed infrastructure (DB, Web, and HA stack) with a single command:

```bash
vagrant up
```
Vagrant will automatically provision the droplets, install Docker/Nginx/Keepalived, and start the MiniTwit containers via Docker Compose on the web nodes. 
      
### Local Development
**Accesing the Servers**

To inspect the internal state of the virtual machines, use Vagrant built in SSH command from the projcet root:

```bash
vagrant ssh webserver
vagrant ssh secondary
vagrant ssh dbserver
```

**Making and Applying Changes**

After editing Python files like minitwit.py on your local machine, the changes are synced to the VM. To apply them to the running service, you must rebuild the Docker image:

```bash
# Inside the webserver/secondary VM
cd /vagrant
docker-compose up --build -d
```

This build flag is essential to re-package the updated source code into th Docker container.

**Monitorying Logs**

To see real-time application logs and debug issues run:

```bash
docker-compose logs -f webserver
```

**Port Configuration**

The foloowing ports are used across our distributed nodes.

        Public Services
        - 80/443: HTTP/HTTPS - Main minitwit application, handled by Nginx. 
        - 3000: Grafana Dashoboards - Visualization of system health and application metrics
        - 9090: Prometheus UI - Direct access to the metrics database and query engine
        - 8080: cAdvisor - Real-time container resource usage and performance metrcis

        Internal Infrastructure Service
        - 5000: Flask App (Gunicorn) - Internal port where the python application listens
        - 27017: MongoDB - Dedicated database server port
        - 3100: Loki - Log aggreagtion system used by Grafana to display logs
        - 22: SSH - Secure shell access for server management and IaC orchestration


## Tech Stack
| Category | Technologies |
|---|---|
| Backend | Python 3.9, Flask, Gunicorn |
| Database | MongoDB 8.0 |
| Infrastructure | DigitalOcean, Vagrant |
| Containerization | Docker, Docker Compose |
| Monitoring & Logging | Prometheus, Grafana, Loki, Alloy, cAdvisor |
| CI/CD & Quality | GitHub Actions, SonarCloud, Flake8 |

## License
[MIT License](License) 







