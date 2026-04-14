#Project Structure

data-engineering/
│
├── api/
│   ├── main.py
│   ├── Dockerfile
│
├── etl/
│   ├── etl.py
│   ├── models.py
│   ├── Dockerfile
│
├── docker-compose.yml
├── .env
├── requirements.txt
├── README.md








 TASK 4: 
1. Scaling (1 Billion Events)

Answer:

Use Kafka for ingestion
Use Spark Streaming / Flink for processing
Store in Data Lake (S3/ADLS)
Use Delta Lake / Iceberg
Deploy on Kubernetes
2. Monitoring

Answer:

Health endpoints in API (/health)
Use:
Prometheus + Grafana
Logs monitoring (ELK stack)
Alerts on:
Failures
Latency
Data drops

3. Recovery (Idempotency)

Answer:

Use Primary Key (instrument_id + timestamp)
Use UPSERT (ON CONFLICT DO NOTHING)
Maintain checkpointing
Re-run pipeline safely without duplicates
