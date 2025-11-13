#!/usr/bin/env python
"""
Quick deployment script for Pixely Partners
Soporta: Heroku, DigitalOcean, AWS, Google Cloud

Usage:
    python deploy.py heroku        # Deploy to Heroku
    python deploy.py digitalocean  # Deploy to DigitalOcean
    python deploy.py aws           # Deploy to AWS
    python deploy.py gcloud        # Deploy to Google Cloud
"""

import os
import subprocess
import sys
from pathlib import Path

class Deployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "pixely-partners"
        
    def run_command(self, cmd, shell=True):
        """Execute a shell command."""
        print(f"\n[*] Running: {cmd}")
        result = subprocess.run(cmd, shell=shell, capture_output=False)
        return result.returncode == 0
    
    def heroku_deploy(self):
        """Deploy to Heroku."""
        print("\n=== Heroku Deployment ===\n")
        
        # Check if heroku CLI is installed
        if not self.run_command("heroku --version", shell=True):
            print("ERROR: Heroku CLI not installed. Install with: npm install -g heroku")
            return False
        
        # Login
        print("\n[*] Please login to Heroku...")
        if not self.run_command("heroku login", shell=True):
            return False
        
        # Create app if not exists
        print(f"\n[*] Creating Heroku app: {self.app_name}...")
        self.run_command(f"heroku create {self.app_name}", shell=True)
        
        # Set environment variables
        print("\n[*] Setting environment variables...")
        openai_key = input("Enter your OPENAI_API_KEY: ")
        if not self.run_command(f'heroku config:set OPENAI_API_KEY="{openai_key}"', shell=True):
            return False
        
        # Initialize Git
        if not Path(".git").exists():
            print("\n[*] Initializing Git...")
            self.run_command("git init", shell=True)
            self.run_command("git add .", shell=True)
            self.run_command('git commit -m "Initial deployment"', shell=True)
        
        # Deploy
        print("\n[*] Deploying to Heroku...")
        if not self.run_command(f"git push heroku main", shell=True):
            print("WARNING: Main branch might not exist, trying master...")
            self.run_command(f"git push heroku master", shell=True)
        
        # Open
        print("\n[*] Opening app in browser...")
        self.run_command("heroku open", shell=True)
        
        print("\n✅ Deployment complete!")
        print(f"App URL: https://{self.app_name}.herokuapp.com/")
        print("\nView logs with: heroku logs --tail")
        
        return True
    
    def digitalocean_deploy(self):
        """Deploy to DigitalOcean."""
        print("\n=== DigitalOcean Deployment ===\n")
        
        # Check if doctl is installed
        if not self.run_command("doctl --version", shell=True):
            print("ERROR: doctl CLI not installed.")
            print("Install from: https://docs.digitalocean.com/reference/doctl/how-to/install/")
            return False
        
        # Create app
        print("\n[*] Creating DigitalOcean app...")
        
        app_spec = {
            "name": self.app_name,
            "services": [
                {
                    "name": "frontend",
                    "github": {
                        "repo": input("Enter GitHub repo (username/repo): "),
                        "branch": "main"
                    },
                    "build_command": "pip install -r requirements.txt",
                    "run_command": "streamlit run frontend/app.py --server.port 8080",
                    "http_port": 8080,
                    "envs": [
                        {
                            "key": "OPENAI_API_KEY",
                            "value": input("Enter OPENAI_API_KEY: ")
                        }
                    ]
                }
            ]
        }
        
        # Save spec to file
        import json
        with open("app.json", "w") as f:
            json.dump(app_spec, f)
        
        print("\n[*] Deploy via DigitalOcean App Platform:")
        print("1. Go to https://cloud.digitalocean.com/apps")
        print("2. Click 'Create App'")
        print("3. Connect GitHub repository")
        print("4. Follow the setup wizard")
        
        return True
    
    def aws_deploy(self):
        """Deploy to AWS."""
        print("\n=== AWS Deployment ===\n")
        
        # Check if AWS CLI is installed
        if not self.run_command("aws --version", shell=True):
            print("ERROR: AWS CLI not installed. Install with: pip install awscli")
            return False
        
        # Configure
        print("\n[*] Configuring AWS CLI...")
        self.run_command("aws configure", shell=True)
        
        # Build Docker image
        print("\n[*] Building Docker images...")
        if not self.run_command("docker build -f Dockerfile.frontend -t pixely-partners-frontend .", shell=True):
            return False
        if not self.run_command("docker build -f Dockerfile.orchestrator -t pixely-partners-orchestrator .", shell=True):
            return False
        
        # Create ECR repositories
        print("\n[*] Creating ECR repositories...")
        self.run_command("aws ecr create-repository --repository-name pixely-partners-frontend --region us-east-1", shell=True)
        self.run_command("aws ecr create-repository --repository-name pixely-partners-orchestrator --region us-east-1", shell=True)
        
        # Login to ECR
        print("\n[*] Logging in to ECR...")
        self.run_command("aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com", shell=True)
        
        print("\n✅ ECR repositories created. Next steps:")
        print("1. Tag your images")
        print("2. Push to ECR")
        print("3. Create ECS Task Definition")
        print("4. Create ECS Service")
        print("\nSee DEPLOYMENT_GUIDE.md for detailed instructions.")
        
        return True
    
    def gcloud_deploy(self):
        """Deploy to Google Cloud."""
        print("\n=== Google Cloud Deployment ===\n")
        
        # Check if gcloud is installed
        if not self.run_command("gcloud --version", shell=True):
            print("ERROR: Google Cloud CLI not installed.")
            print("Install from: https://cloud.google.com/sdk/docs/install")
            return False
        
        # Authenticate
        print("\n[*] Authenticating with Google Cloud...")
        self.run_command("gcloud auth login", shell=True)
        
        # Create project
        project_id = input("Enter Google Cloud Project ID: ")
        print(f"\n[*] Setting project to {project_id}...")
        self.run_command(f"gcloud config set project {project_id}", shell=True)
        
        # Enable APIs
        print("\n[*] Enabling required APIs...")
        self.run_command("gcloud services enable run.googleapis.com", shell=True)
        self.run_command("gcloud services enable cloudbuild.googleapis.com", shell=True)
        
        # Deploy to Cloud Run
        print("\n[*] Deploying to Cloud Run...")
        openai_key = input("Enter OPENAI_API_KEY: ")
        
        self.run_command(
            f"gcloud run deploy pixely-frontend "
            f"--source . "
            f"--build-config cloudbuild.yaml "
            f"--platform managed "
            f"--region us-central1 "
            f"--allow-unauthenticated "
            f'--set-env-vars OPENAI_API_KEY="{openai_key}"',
            shell=True
        )
        
        print("\n✅ Deployment to Google Cloud complete!")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [heroku|digitalocean|aws|gcloud]")
        sys.exit(1)
    
    platform = sys.argv[1].lower()
    deployer = Deployer()
    
    if platform == "heroku":
        success = deployer.heroku_deploy()
    elif platform == "digitalocean":
        success = deployer.digitalocean_deploy()
    elif platform == "aws":
        success = deployer.aws_deploy()
    elif platform == "gcloud":
        success = deployer.gcloud_deploy()
    else:
        print(f"Unknown platform: {platform}")
        print("Available: heroku, digitalocean, aws, gcloud")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
