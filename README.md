# AWS AI Inference Service

A containerized PyTorch image-classification API deployed on AWS ECS Fargate, with performance benchmarking comparing local Docker execution against cloud deployment.

## Project Overview

This project demonstrates an end-to-end AI inference deployment workflow, from building a model-serving API to containerization, cloud deployment, and performance evaluation.

The service uses a pretrained MobileNetV2 model to perform image classification through a REST API.

## Architecture

```text
                  Client
                    |
                    v
             FastAPI REST API
               /predict
                    |
                    v
             PyTorch Model
               MobileNetV2
                    |
                    v
              Prediction
                    |
                    v
                JSON Response

        Deployment Infrastructure

        Docker Container
               |
               v
          Amazon ECR
               |
               v
         ECS Fargate Task
               |
               v
          CloudWatch Logs
```

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Deep Learning | PyTorch, TorchVision |
| API | FastAPI, Uvicorn |
| Containerization | Docker |
| Cloud | AWS ECS Fargate, Amazon ECR |
| Monitoring | Amazon CloudWatch |
| Load Testing | Locust |

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Service information |
| `/health` | GET | Health check |
| `/predict` | POST | Image classification |

The prediction endpoint accepts an image using multipart form-data with the field name `file` and returns the predicted ImageNet class and confidence score.

## Run Locally

Build the Docker image:

```bash
docker build -t aws-ai-inference:v1 .
```

Run the container:

```bash
docker run -d --name ai-api -p 8000:8000 aws-ai-inference:v1
```

Check service health:

```bash
curl http://localhost:8000/health
```

Stop the container:

```bash
docker stop ai-api
```

## AWS Deployment

The application was deployed using:

- Amazon ECR for Docker image storage.
- Amazon ECS with AWS Fargate for serverless container execution.
- 1 vCPU and 3 GB memory for the Fargate task.
- Amazon CloudWatch Logs for application logging.

The deployment was tested in AWS US East (Ohio), using a standalone Fargate task.

## Performance Benchmarking

Locust was used to compare local Docker and AWS Fargate performance under 1, 5, and 10 concurrent users.

| Environment | Users | Requests/sec | Average latency | p95 latency |
|---|---:|---:|---:|---:|
| Local Docker | 1 | 14.49 | 68.5 ms | 130 ms |
| AWS Fargate | 1 | 9.43 | 105.9 ms | 120 ms |
| Local Docker | 5 | 34.37 | 145.4 ms | 240 ms |
| AWS Fargate | 5 | 22.45 | 222.5 ms | 280 ms |
| Local Docker | 10 | 34.61 | 288.8 ms | 520 ms |
| AWS Fargate | 10 | 19.56 | 510.6 ms | 820 ms |

**Key observations:**

- All six benchmark runs completed with zero failed requests.
- Local throughput plateaued at approximately 34.5 requests/sec between 5 and 10 users.
- Fargate throughput peaked at approximately 22.4 requests/sec with 5 users.
- At 10 concurrent users, Fargate latency increased substantially.
- The results suggest potential CPU and concurrency bottlenecks that warrant further investigation.

**Benchmark limitation:** The Fargate tests were executed from Edmonton, Canada, against a service hosted in Ohio. Therefore, remote measurements include network latency and should not be interpreted as isolated model-inference performance.

Detailed benchmark methodology and raw Locust CSV results are available in [`benchmarks/`](benchmarks/).

## Repository Structure

```text
aws-ai-inference/
├── app/
│   └── main.py
├── tests/
│   ├── locustfile.py
│   └── load_test.jpg
├── benchmarks/
│   ├── README.md
│   └── results/
├── Dockerfile
├── requirements.txt
├── task-definition.json
├── ecs-task-trust-policy.json
├── .dockerignore
└── .gitignore
```

## Future Improvements

- Evaluate multiple Uvicorn workers and container resource configurations.
- Investigate CPU utilization and inference concurrency.
- Add automated testing and CI/CD.
- Explore horizontal scaling with ECS services.
- Evaluate model optimization techniques such as ONNX Runtime and quantization.

## Author

AI / Machine Learning Engineer | Medical Imaging | Computer Vision | Embedded Systems

This is a personal portfolio project demonstrating practical AI model deployment and cloud performance evaluation.