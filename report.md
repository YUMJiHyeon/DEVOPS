## DevOps, Software Evolution and Software Maintenance 
### Cousre code: KSDSESM1KU

#### Exam assignment by:

Erle Sognnæs:
s25128@itu.dk

Jihyeon Yum:
s25126@itu.dk

Margrét Edda Friðgeirsdóttir:
s25117@itu.dk

Mathias Anakin Alm:
matal@itu.dk



 ### (Formal Requirements)
	Make sure that you link all artifacts that you consider constitutional to your projects together with short descriptions of the linked artifacts from your reports, i.e., link all necessary repositories, issue trackers, monitoring/logging systems, etc.


	Since this is a group project and the report is written by a group make sure to indicate for each section the respective author(s).


 ### 1) Introduction? (What to include in the report? )

 ### 2) System's Perspective (Architecture)

	F.ex:
#### 2.1) System Architecture

#### 2.2) System Design

#### 2.3) Dependencies
The system is implemented mainly in Python using the Flask web framework. It uses MongoDB as the database through PyMongo. Passwords are handled with Werkzeug security utilities. Monitoring is supported through Prometheus using prometheus_client and prometheus_flask_exporter. The application is containerized with Docker and orchestrated through Docker Compose. Development and version control are handled with Git and GitHub, while CI/CD is handled through GitHub Actions. Code quality/security analysis is configured through Sonar using sonar-project.properties.


#### 2.4) Current state
 
	A description and illustration of the:

		Design and architecture of your ITU-MiniTwit systems.
		- Diagrams:
				- Module View
				- C&C View
				- Allocation View
#### Allocation View
![Allocation View](img/UML-Deployment-Diagram.png "Allocation view")

As seen in the Allocation View above, our system is split into three layers. We have the frontend/UI layer, which consists of the MiniTwit browser application that we received at the beginning of the course. The logic layer is comprised of two web servers: a primary web server and a secondary web server. We implemented Docker containers to run our application together with all required dependencies, ensuring that the application remains consistent across different servers and environments. We also implemented Gunicorn, which hosts the MiniTwit Flask application. Gunicorn handles incoming HTTP requests before forwarding them to the main application. Both web servers communicate with the MongoDB database server, which stores the application’s data. Finally, Prometheus monitors the system by scraping metrics data from the web servers. As a side note, our system is not a perfectly separated three-layer architecture, since parts of the logic layer also interact directly with the data layer.

#### Module View diagram
![Module view](img/moduleviewdig.png "Module view")

The core of the application logic is handled by minitwit.py, which maps incoming web traffic to spesific python function. As shown in the diagram, we organized our main application features into different logical sections. Authentication controls user registration and login, Message handles posting new tweets or retweeting others posts, Follow handles starting to follow or unfollowing other users, Timeline queries the database to build the public and personal feeds. We also have a Metrics module that hooks into our Prometheus configuration to track system performance. All these functional pieces feed down into a shared data-access tier, MongoDB access, which is the "last stop" for the information before it translates to code readable for the database, and reaches the storage.


		All dependencies of your ITU-MiniTwit systems on all levels of abstraction and development stages. That is, list and briefly describe all technologies and tools you applied and depend on.
		Describe the current state of your systems, for example using results of static analysis and quality assessments.

 ### 3) Process' perspective
		This perspective should clarify how code or other artifacts come from idea into the running system and everything that happens on the way.

		In particular, the following descriptions should be included:

		A complete description and illustration of stages and tools included in the CI/CD pipelines, including deployment and release of your systems.
			- Diagram: CI/CD Pipeline

#### CI/CD Pipeline diagram
![CI/CD pipeline](img/cicddig.png "CI/CD pipeline")
As seen in the diagram above our CI/CD pipeline starts when a developer pushes their code onto our Github reposoitory. Then the Github Actions is activated and and the tests and are run automaticlly and in parellel. 

The pipeline includes automated build processes, dynamic page deployments, SonarCloud static code analysis, CodeQL security analysis, and Docker image build and scan operations. These automated checks help ensure code quality, security, and deployment consistency before changes are merged into the main branch.

Once all checks have successfully passed, the changes are merged into the main branch. The updated application is then deployed to both the primary web server and the secondary web server using Docker Compose restart procedures.

This CI/CD pipeline automates large parts of the development and deployment workflow, reducing manual configuration errors and supporting continuous integration and continuous deployment practices.



		How do you monitor your systems and what precisely do you monitor?

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
The user- and tweet total were pretty straight foward as we used these two simple PromQL queries: max(minitwit_users_total), rate(minitwit_tweets_total[1m]). For our CPU monotroing we used the following query: sum(rate(container_cpu_usage_seconds_total{id!="/"}[1m])) by (name) * 100. But that helped us see our resource consumption and preformance bottlenecks for induvidual containers. 

![Monotoring dashboard](img/monotoring.gif "monotoring dashboard")



		### here we can refrence our demo vidos, explain our loggin further.
		
#### Demo videos here
		What do you log in your systems and how do you aggregate logs?
		Brief description of how you security hardened your systems.
			- .dockerignore- and .env-files to keep sensitive information to getting uploaded online.
		How do you handle availability and scaling in your systems?

 ### 4) Reflection Perspective
	Describe the biggest issues, how you solved them, and which are major lessons learned with regards to:

		- evolution and refactoring
		- operation, and maintenance of your ITU-MiniTwit systems. 
			 - Link back to respective commit messages, issues, tickets, etc. to illustrate these.

	Also reflect and describe what was the "DevOps" style of your work. For example, what did you do differently to previous development projects and how did it work?



#### 1.) TODO: Assure Information Correctness 

#### 2.) TODO: Polish Project Repositories and Documentation 

#### 2.1.) Create a .mailmap file in the root of your repositories 

#### 2.2.) TODO: Create Four Videos Demonstrating your ITU-MiniTwit System in Production 



	b) Logging Dashboards in Action: Create another screen recording that provides an overview over all your logging dashboards from the production system. That is, demonstrate that the logging information in the dashboards changes over time, the more data is received from the simulator.
![Logging dashboard](img/logging.gif "logging dashboard")

	c) IaC in Action: Create a third screen recording that shows your infrastructure as code, configuration management in action. This video should demonstrate that infrastructure can be spun-up from scratch and that it is configured accordingly. That is, something like vagrant up from your command line or a CI/CD pipeline.

	d) CI/CD in Action: With infrastructure up and running, this last video should demonstrate how a change that is implemented in a feature branch, is deployed to production after traversing your CI/CD pipeline. That is, this video should start from checking out your code repository and applying a tiny change in a feature branch, how that change is pushed to the repository, how it is picked up by the CI/CD pipeline, i.e., tested and automatically deployed to production.

#### 2.3.) TODO: Update the main readme file 
	
TODO: System's Perspective 

TODO: Process' perspective 

TODO: Reflection Perspective 

TODO: Use of Generative AI -> ✨ YES ✨ 

 idea: We used it when we got stuck or encountered unexpected errors.  It has been a life saver for the most part.  

