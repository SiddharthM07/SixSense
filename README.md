 SixSense – Cricket Match Prediction with Observability
=========================================================

SixSense is a cricket match prediction web app that allows users to select players and predict match outcomes. With the IPL season in full swing, I wanted to utilize my DevOps skills to build something fun, practical, and technically robust.
________________________________________
Technologies Used
=================
Breakdown by layers:
•	Frontend: FastAPI + Jinja2
•	Backend: Python
•	Containerization: Docker
•	Orchestration: Kubernetes (Minikube)
•	CI/CD: Jenkins
•	Database: Supabase (PostgreSQL)
•	Monitoring: Prometheus + Grafana
•	Cloud/Infra: AWS EC2 (via Terraform)
________________________________________
 Features
 ==========
•	Interactive match prediction interface with real-time player selection
•	App fully containerized and deployed using Minikube
•	Secrets managed securely via Jenkins credentials to avoid hardcoding
•	CI/CD pipeline implemented with Jenkins
•	Custom CPU & Memory utilization alerts using Grafana
•	Prometheus integrated for monitoring pod-level metrics
________________________________________
 Monitoring & Alerting
 =====================
•	Metrics Collected: CPU, Memory (pod-level)
•	/metrics Endpoint: Created to expose internal app metrics to Prometheus
•	Tools Used: Prometheus (scraping), Grafana (visualization & alerting)
•	Alerts: Custom alerts configured in Grafana for resource usage thresholds
________________________________________
 Deployment
 =============
•	Application containerized with Docker
•	Deployed to a local Kubernetes cluster using Minikube
•	Infrastructure provisioned using Terraform (VPC, EC2, Security Groups)
•	Jenkins automates the build, push, and deployment process
________________________________________
 Learnings & Challenges
 =========================
•	Initially imported API keys and database URLs using a .env file, which wasn't ideal. Switched to using Jenkins credentials and injected them securely through the pipeline.
•	Faced several issues during implementation — leveraged ChatGPT (shoutout!) to debug and overcome most of them.
•	Gained hands-on experience in end-to-end DevOps flow, from infrastructure provisioning to monitoring and alerting.
________________________________________

 
==>Incase you’re using minikube on your machine locally forward the port as below
kubectl port-forward svc/sixsense-service 9092:5001
Forwarding from 127.0.0.1:9092 -> 5001
Forwarding from [::1]:9092 -> 5001


________________________________________
