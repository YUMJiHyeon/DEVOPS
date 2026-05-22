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


This report details the design, evolution, and operation of the ITU-MiniTwit system for the 'DevOps, Software Evolution, and Software Maintenance' course. Our group aimed to transform the legacy application into a robust, scalable service by applying modern DevOps principles.


## Overview 
### a) Monitoring Dashboards in Action
![Monotoring dashboard](img/monotoring.gif "monotoring dashboard")
This video shows our monitoring dashboard on Grafana in action, visualizing real-application metrics and health collectied via Prometheus as system processes traffic from the simulator.

### b) Logging Dashboards in Action
![Logging dashboard](img/logging.gif "logging dashboard")
This video shows our logging dashboard on Grafana in action, utilizing Loki to aggregate and display real-time event logs as the system processes traffic from the simulator.

### c) IaC in Action
![IaC in Action](img/IaC5.gif "IaC in Action")	
This video shows the automated creation of three servers using Vagrant and the DigitalOcean provider. The shell provisiong scripts installing essential softwares. It also shows the Minitwit application being deployed and executed via Docker on both the primary and secondary servers.

### d) CI/CD in Action
![CI/CD pipeline gif](img/CiCdPl.gif "CI/CD pipeline gif")
This video shows our CI/CD pipeline using GitHub Actions. Once merged into the main branch, the pipeline automatically connects to our production droplets via SSH to deploy the changes by restarting the Docker containers with the updated image.

## Deployment
### Live System
The applicatino is currently hosted at [here](https://devopsgroupo.me)
### Infrastructure
We use DigitalOcean for the VPS droplet. Domain management and DNS resolution are handled through DigitalOcean. Implemented using Keepalived and Nginx to manage a Virtual IP (VIP: 129.212.212.105) for automated failover between the primary and secondary nodes. A distributed MongoDB instance running on a dedicated database server.

## Installation
### a) Prerequisties

    Vagrant & DigitalOcean Provider plugin 
    DigitalOcean API Token
    SSH Private Key
    
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

### d) Usage
To deploy the entire distributed infrastructure (DB, Web, and HA stack) with a single command:

```bash
vagrant up
```
Vagrant will automatically provision the droplets, install Docker/Nginx/Keepalived, and start the MiniTwit containers via Docker Compose on the web nodes. 
      
### e) Local Development
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


