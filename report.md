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



 ### (Formal Requirements - remove)
Make sure that you link all artifacts that you consider constitutional to your projects together with short descriptions of the linked artifacts from your reports, i.e., link all necessary repositories, issue trackers, monitoring/logging systems, etc.

Since this is a group project and the report is written by a group make sure to indicate for each section the respective author(s).


 ## Table of content
	* **[1. Introduction](#1-introduction)** — Executive summary of the report scope and objectives.
* **[2. System's Perspective (Architecture)](#2-systems-perspective-architecture)** — The physical blueprint and software patterns of the application.
  * *[2.1 System Architecture](#21-system-architecture)* — High-level infrastructure tiering via our Allocation View.
  * *[2.2 System Design](#22-system-design)* — Component logic breakdowns using Module and Sequence views.
  * *[2.3 Dependencies](#23-dependencies)* — Frameworks, tools, and technical requirements.
  * *[2.4 Current State](#24-current-state)* — Current operational status, metrics, and technical debt analysis.
* **[3. Process Perspective](#3-process-perspective)** — Lifecycles tracing how changes move safely from an idea to production.
  * *[3.1 Infrastructure as Code (IaC)](#31-infrastructure-as-code-iac)* — Automated provisioning workflows.
  * *[3.2 CI/CD Pipeline](#32-cicd-pipeline)* — Continuous testing, validation, and rolling container deployments.
  * *[3.3 Monitoring](#33-monitoring)* — Systems observability using Prometheus and custom PromQL metrics.
  * *[3.4 Logging](#34-logging)* — Centralized log aggregation with Grafana Loki.
  * *[3.5 Security Hardening](#35-security-hardening)* — Isolation practices for environment variables and secrets.
  * *[3.6 Availability and Scaling](#36-availability-and-scaling)* — High availability tactics through multi-server design.
* **[4. Reflection Perspective](#4-reflection-perspective)** — Engineering challenges faced, lessons learned, and our interpretation of "DevOps style" work.

 
 ## 1) Introduction
 
		
## 2) System's Perspective (Architecture)

A description and illustration of the:
	-Design and architecture of your ITU-MiniTwit systems.
	-All dependencies of your ITU-MiniTwit systems on all levels of abstraction and development stages. That is, list and briefly describe all technologies and tools you applied and depend on.
	-Describe the current state of your systems, for example using results of static analysis and quality assessments.

### 2.1) System Architecture

#### Allocation View
![Allocation View](img/UML-Deployment-Diagram.png "Allocation view")

As seen in the Allocation View above, our system is split into three layers. We have the frontend/UI layer, which consists of the MiniTwit browser application that we received at the beginning of the course. The logic layer is comprised of two web servers: a primary web server and a secondary web server. We implemented Docker containers to run our application together with all required dependencies, ensuring that the application remains consistent across different servers and environments. We also implemented Gunicorn, which hosts the MiniTwit Flask application. Gunicorn handles incoming HTTP requests before forwarding them to the main application. Both web servers communicate with the MongoDB database server, which stores the application’s data. Finally, Prometheus monitors the system by scraping metrics data from the web servers. As a side note, our system is not a perfectly separated three-layer architecture, since parts of the logic layer also interact directly with the data layer.

### 2.2) System Design

For this project we used Flask which is a lightweight Python web framwork. It was chosen as it was recommended to us for this project and provided us a simple way to build the MiniTwit application in Python. Flask was used to implement routing, user authentication, and database integration. For the frontend it shows all the pages the users sees using HTML templates that we get from Jinja2, Flasks template engine. It also sends data from Python into the HTML like tweets and usernames. Flask has a internal support library Wekzeug. In our project it used for securely hashing passwords, validating requests, handling sessions and routing internally. 

Regarding the backend, Flask handles all user requests and responses such as log ins, tweets, follow requests and logouts. Flask takes those requests and sends them to Flask-PyMongo which we use to send and recive data from our MongoDB server. Flask-PyMongo is built on top of PyMongo which is the official Python driver for MongoDB which allows us to access low-level functionality in our data base. 


#### Module View
![Module view](img/moduleviewdig.png "Module view")

The core of the application logic is handled by minitwit.py, which maps incoming web traffic to spesific python function. As shown in the diagram, we organized our main application features into different logical sections. Authentication controls user registration and login, Message handles posting new tweets or retweeting others posts, Follow handles starting to follow or unfollowing other users, Timeline queries the database to build the public and personal feeds. We also have a Metrics module that hooks into our Prometheus configuration to track system performance. All these functional pieces feed down into a shared data-access tier, MongoDB access, which is the "last stop" for the information before it translates to code readable for the database, and reaches the storage. This modular structure improves maintainability by separating responsibilities into focused components. It also simplifies testing and future development, since changes to one feature area can often be made without affecting unrelated parts of the system.



#### Component and Connector view  
![Component and Connector view](img/c&cdiagram.png "Component and Connector view")

This sequence diagram shows the lifecycle of registering a user in our system. The prosess starts when a client, either a User or a Simulator, sends their information through clicking submit. Gunicorn catches the data and forwards it to our Flask application. Flask queries MongoDB with find_one to look for the username in the database, and MongoDB returns if the username is taken or not.
Here the logic splits into alternative branches.
- Path A represents when the username is taken. If this is the case, execution stops and an error message is sent through the system which is shown to the user as "The username is already taken"
- Path B represents when the username is free. In this case Flask hashes the password, and sends insert_one to the database.

After successful registration the execution enters the inner alternative block, which handles whether the registration is done by a Simulator or a Human User.
- Path B1 represents if the client is a Simulator. The system returns an empty string and a HTTP 204 to register the success, but not use necessary internet speed with opening the login page.
- Path B2 represents if the client is a Human user. Then Flask activates the redirect function, which sends the user to the login page.



### 2.3) Dependencies
Note (remove): All dependencies of your ITU-MiniTwit systems on all levels of abstraction and development stages. That is, list and briefly describe all technologies and tools you applied and depend on.

The system is implemented mainly in Python using the Flask web framework. It uses MongoDB as the database through PyMongo. Passwords are handled with Werkzeug security utilities. Monitoring is supported through Prometheus using prometheus_client and prometheus_flask_exporter. The application is containerized with Docker and orchestrated through Docker Compose. Development and version control are handled with Git and GitHub, while CI/CD is handled through GitHub Actions. Code quality/security analysis is configured through Sonar using sonar-project.properties.

Our deployment dependencies are illustrated in our Allocation view diagram. 



### 2.4) Current state
Note (remove): Describe the current state of your systems, for example using results of static analysis and quality assessments.

| Area             | Current state                            |
| ---------------- | ---------------------------------------- |
| Web framework    | Flask                                    |
| Database         | MongoDB via Flask-PyMongo/PyMongo        |
| Testing          | Pytest and Selenium                      |
| Static analysis  | Flake8                                   |
| Formatting       | Black                                    |
| Deployment       | Gunicorn                                 |
| Monitoring       | Prometheus exporter                      |
| Main improvement | Record actual test/lint results in CI/CD |



## 3) Process perspective
Note (remove): This perspective should clarify how code or other artifacts come from idea into the running system and everything that happens on the way.

In particular, the following descriptions should be included:

A complete description and illustration of stages and tools included in the CI/CD pipelines, including deployment and release of your systems.
	- Diagram: CI/CD Pipeline


### 3.1) Infrastructure as Code (IaC)

#### IaC in Action
![IaC in Action](img/IaC5.gif "IaC in Action")	


### 3.2) CI/CD Pipeline

![CI/CD pipeline](img/cicddig.png "CI/CD pipeline")
As seen in the diagram above our CI/CD pipeline starts when a developer pushes their code onto our Github reposoitory. Then the Github Actions is activated and and the tests and are run automaticlly and in parellel. 

The pipeline includes automated build processes, dynamic page deployments, SonarCloud static code analysis, CodeQL security analysis, and Docker image build and scan operations. These automated checks help ensure code quality, security, and deployment consistency before changes are merged into the main branch.

Once all checks have successfully passed, the changes are merged into the main branch. The updated application is then deployed to both the primary web server and the secondary web server using Docker Compose restart procedures.

This CI/CD pipeline automates large parts of the development and deployment workflow, reducing manual configuration errors and supporting continuous integration and continuous deployment practices.

#### CI/CD in Action
![CI/CD pipeline gif](img/CiCdPl.gif "CI/CD pipeline gif")


### 3.3) Monitoring (How do you monitor your systems and what precisely do you monitor? - remove)

We monitored our system by keeping track of logging, our webservers CPU usage, the total of users in our system, the rate of which users tweeted as well as our HTTP requests. For logging we used Grafana Loki while for the rest we used Grafana Prometheus. We tracked 4 diffrent types of HTTP requests such as: 

		- successful request (200)
		- redirects (302) 
		- missing routes (404) 
		- unsupported request methhods (405)
		
Our monotoring also help us see some unusual requests such as:

		- BXJZ
		- HIAS 
		- PROPFIND
		
These were most likely vulnerability-scanning traffic against our server. 
The user- and tweet total were pretty straight foward as we used these two simple PromQL queries: max(minitwit_users_total), rate(minitwit_tweets_total[5m]). For our CPU monotroing we used the following query: sum(rate(container_cpu_usage_seconds_total{id!="/"}[1m])) by (name) * 100. But that helped us see our resource consumption and preformance bottlenecks for induvidual containers. 


#### Monitoring Dashboard in Action
![Monotoring dashboard](img/monotoring.gif "monotoring dashboard")


### 3.4) Logging
(here we can refrence our demo vidos, explain our loggin further.
What do you log in your systems and how do you aggregate logs?)

#### Logging Dashboards in Action
![Logging dashboard](img/logging.gif "logging dashboard")


		
### 3.5) Security hardening
Brief description of how you security hardened your systems.
- .dockerignore- and .env-files to keep sensitive information to getting uploaded online.

### 3.6) Availability and scaling
How do you handle availability and scaling in your systems?


 ## 4) Reflection Perspective
	Describe the biggest issues, how you solved them, and which are major lessons learned with regards to:

		- evolution and refactoring
		- operation, and maintenance of your ITU-MiniTwit systems. 
			- Link back to respective commit messages, issues, tickets, etc. to illustrate these.

	Also reflect and describe what was the "DevOps" style of your work. For example, what did you do differently to previous development projects and how did it work?



#### 1.) TODO: Assure Information Correctness 

#### 2.) TODO: Polish Project Repositories and Documentation 

#### 2.1.) Create a .mailmap file in the root of your repositories 

#### 2.2.) Create Four Videos Demonstrating your ITU-MiniTwit System in Production 


#### 2.3.) TODO: Update the main readme file 
	
TODO: System's Perspective 

TODO: Process' perspective 

TODO: Reflection Perspective 

TODO: Use of Generative AI -> ✨ YES ✨ 

 idea: We used it when we got stuck or encountered unexpected errors.  It has been a life saver for the most part.  

