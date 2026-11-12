\# AI Inference Benchmark: Local Docker vs AWS Fargate



\## 1. Objective



Evaluate the performance of a containerized image-classification API under concurrent HTTP requests, comparing local Docker execution with deployment on AWS ECS Fargate.



The API uses FastAPI, PyTorch, and a pretrained MobileNetV2 model for image classification.



\## 2. Test Environment



\### Local Environment

\- CPU: Intel Core i7-10750H (6 cores / 12 logical processors)

\- RAM: 8 GB

\- Runtime: Docker Desktop

\- API: FastAPI + Uvicorn

\- Inference: PyTorch / MobileNetV2

\- Device: CPU



\### AWS Environment

\- Platform: Amazon ECS on AWS Fargate

\- Region: us-east-2 (Ohio)

\- CPU allocation: 1 vCPU

\- Memory allocation: 3 GB

\- Container port: 8000

\- Inference: CPU

\- Deployment: Single Fargate task



\## 3. Benchmark Methodology



Locust was used to generate concurrent HTTP requests against the `/predict` endpoint.



| Parameter | Configuration |

|---|---|

| Load testing tool | Locust 2.47.0 |

| Endpoint | POST /predict |

| Concurrent users | 1, 5, 10 |

| Ramp-up rate | 1 user/second |

| Test duration | 70 seconds |

| User wait time | 0 seconds |

| Image payload | tests/load\_test.jpg |

| Request type | Multipart image upload |



The same Locust test script and image payload were used in both environments.



The Locust client ran on the local computer. Therefore, AWS measurements include network latency between Edmonton, Canada, and AWS Ohio.



These results represent end-to-end API performance, not isolated model inference time.



\## 4. Benchmark Results



\### Throughput (Requests per Second)



| Concurrent Users | Local Docker | AWS Fargate |

|---:|---:|---:|

| 1 | 14.49 | 9.43 |

| 5 | 34.37 | 22.45 |

| 10 | 34.61 | 19.56 |



\### Latency (milliseconds)



| Users | Environment | Average | p50 | p95 | p99 | Maximum |

|---:|---|---:|---:|---:|---:|---:|

| 1 | Local | 68.5 | 72 | 130 | 210 | 1853 |

| 1 | Fargate | 105.9 | 100 | 120 | 210 | 519 |

| 5 | Local | 145.4 | 120 | 240 | 310 | 506 |

| 5 | Fargate | 222.5 | 260 | 280 | 350 | 676 |

| 10 | Local | 288.8 | 250 | 520 | 640 | 1225 |

| 10 | Fargate | 510.6 | 410 | 820 | 1400 | 2092 |



\### Reliability



| Concurrent Users | Local Failures | Fargate Failures |

|---:|---:|---:|

| 1 | 0 | 0 |

| 5 | 0 | 0 |

| 10 | 0 | 0 |



All six benchmark runs completed with zero failed requests.



The figures are taken from the Locust aggregate CSV files. Minor differences from terminal summaries can occur because the CSV aggregate is used as the reporting source.



\## 5. Engineering Observations



\### Local Docker

\- Throughput increased from 14.49 RPS at one user to 34.37 RPS at five users.

\- Increasing concurrency from five to ten users produced almost no additional throughput.

\- p95 latency increased from 240 ms to 520 ms between five and ten users.

\- This suggests a CPU or application concurrency bottleneck under higher load.



\### AWS Fargate

\- Throughput peaked at approximately 22.45 RPS with five concurrent users.

\- At ten users, throughput decreased to 19.56 RPS.

\- Average latency increased from 222.5 ms at five users to 510.6 ms at ten users.

\- p95 latency reached 820 ms and p99 reached 1400 ms at ten users.

\- The single-task, 1-vCPU configuration appears constrained under heavier concurrency.



\### Local vs Cloud

The local environment achieved higher throughput in these tests. However, this is not a direct hardware-only comparison:

\- The local computer has six physical CPU cores.

\- Fargate was configured with one vCPU.

\- Remote requests include network latency.

\- The test used one Fargate task without horizontal scaling.



A larger Fargate CPU allocation or multiple task instances should be evaluated separately.



\## 6. Limitations and Future Experiments



This is an initial performance benchmark, not a statistically comprehensive capacity study.



Potential follow-up experiments:



1\. Compare Fargate configurations with 1, 2, and 4 vCPUs.

2\. Measure CPU and memory utilization through CloudWatch.

3\. Compare one task against multiple tasks behind an Application Load Balancer.

4\. Evaluate Uvicorn worker counts and CPU thread settings.

5\. Separate image preprocessing, model inference, and network latency.

6\. Repeat tests multiple times and report variability.

7\. Evaluate autoscaling based on CPU utilization or request load.



\## 7. Reproducing the Tests



From the project root, start the local API and run:



```powershell

docker run --rm `

&#x20; --mount "type=bind,source=$((Get-Location).Path)\\tests,target=/mnt/locust/tests" `

&#x20; --mount "type=bind,source=$((Get-Location).Path)\\benchmarks\\results,target=/mnt/locust/results" `

&#x20; locustio/locust:2.47.0 `

&#x20; -f /mnt/locust/tests/locustfile.py `

&#x20; --headless `

&#x20; -H http://host.docker.internal:8000 `

&#x20; -u 5 -r 1 -t 70s `

&#x20; --reset-stats `

&#x20; --csv /mnt/locust/results/local\_u5 `

&#x20; --csv-full-history

```



Change `-u 5` to `1` or `10` to reproduce the other concurrency levels.



For AWS testing, replace the host with the reachable Fargate task endpoint and use the corresponding `fargate\_u1`, `fargate\_u5`, or `fargate\_u10` output prefix.



Stop the Fargate task after testing to avoid unnecessary compute charges.



\## 8. Project Structure



```text

aws-ai-inference/

├── app/

│   └── main.py

├── tests/

│   ├── locustfile.py

│   └── load\_test.jpg

├── benchmarks/

│   ├── README.md

│   └── results/

├── Dockerfile

└── requirements.txt

```



\## 9. Conclusion



This benchmark demonstrates a complete containerized AI inference workflow deployed locally and on AWS ECS Fargate.



Both environments maintained zero request failures across the tested concurrency levels. The results also reveal a throughput plateau locally and a more pronounced performance limitation on the single-vCPU Fargate task.



The next optimization step is to measure resource utilization and evaluate CPU scaling before introducing more complex infrastructure.

