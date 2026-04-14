 Setup Instructions

1. Clone the repository:



2. Create `.env` file (based on reference):

```bash
cp .env.example .env
```

3. Update `.env`:

```env
DB_NAME=market
DB_USER=postgres
DB_PASS=postgres
```

4. Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

---

##  How to Run the System

Run the following command from project root:

```bash
docker-compose up --build
```

This will start:

* FastAPI server (API)
* PostgreSQL database
* ETL pipeline

---
##  API Example

**Endpoint:**

```http
GET /v1/market-data
```

**Sample Response:**

```json
[
  {
    "instrument_id": "AAPL",
    "price": 172.21,
    "volume": 120.5,
    "timestamp": "2026-03-12T10:00:00Z"
  }
]
```

---

##  Fault Injection (Chaos Engineering)

To simulate real-world failures:

* **5% of requests are faulty**

  * **2.5%** → HTTP 500 Internal Server Error
  * **2.5%** → Malformed data (e.g., `"price": "INVALID"`)

 Purpose:

* Test ETL resilience
* Validate retry and error handling logic

---

##  Database Schema

**Table:** `market_data`

| Column        | Type      | Description         |
| ------------- | --------- | ------------------- |
| instrument_id | TEXT      | Stock/Crypto ticker |
| price         | FLOAT     | Market price        |
| volume        | FLOAT     | Trade volume        |
| timestamp     | TIMESTAMP | Record time         |
| vwap          | FLOAT     | Calculated VWAP     |
| is_outlier    | BOOLEAN   | Outlier flag        |

**Primary Key:**

```sql
(instrument_id, timestamp)
```

---

##  ETL Pipeline Details

###  Extraction

* Polls API every few seconds
* Handles:

  * Network timeouts
  * API failures
  * Fault injection errors

---

###  Schema Validation

* Uses **Pydantic models**
* Drops invalid records

---

###  Transformation

#### VWAP Calculation

```text
VWAP = Σ(price × volume) / Σ(volume)
```

####  Outlier Detection

* Flag records where:

```text
|price - avg_price| > 15%
```

---

### Load & Logging

* Inserts data using:

```sql
ON CONFLICT DO NOTHING
```

* Ensures:

  * No duplicates
  * Idempotent processing

* Logs include:

  * records_processed
  * records_dropped
  * execution_time

---

##  Docker Infrastructure

### Services:

* **api**

  * FastAPI service
  * Port: 8000

* **etl**

  * Python ETL pipeline
  * Runs continuously

* **db**

  * PostgreSQL database

---

##  Docker Networking

* ETL connects to DB using:

```text
host = db
```

* API accessed internally via:

```text
http://api:8000
```

---

##  System Flow

1. API generates synthetic data
2. Fault injection simulates failures
3. ETL fetches and validates data
4. Applies VWAP + outlier logic
5. Stores clean data in PostgreSQL
6. Logs processing metrics

---

##  ETL Log Examples

```json
{
  "level": "INFO",
  "message": "Batch processed",
  "records_processed": 10,
  "records_dropped": 2,
  "execution_time_seconds": 1.5
}
```

---

##  Error Handling Logs

```json
{
  "level": "WARNING",
  "message": "API request failed, retrying..."
}
```

```json
{
  "level": "WARNING",
  "message": "Validation failed for record"
}
```

---

## Database Queries

###  Check Record Count

```sql
SELECT COUNT(*) FROM market_data;
```

---

### 🔹 View Latest Records

```sql
SELECT * FROM market_data
ORDER BY timestamp DESC
LIMIT 5;
```

---

### Find Outliers

```sql
SELECT * FROM market_data WHERE is_outlier = true;
```

---

###  VWAP Analysis

```sql
SELECT instrument_id, AVG(vwap)
FROM market_data
GROUP BY instrument_id;
```

---

## System Monitoring

###  Health Checks

* API:

```bash
curl http://localhost:8000/v1/market-data
```

* Database:

* Verify connection + table

* ETL:

* Check logs for "Batch processed"

---

###  Metrics

* Throughput → records/sec
* Error rate → failed batches
* Latency → processing time

---

##  Docker Monitoring

```bash
docker-compose ps
docker-compose logs api
docker-compose logs etl
docker-compose logs db
```

---

##  Troubleshooting

###  ETL cannot connect to API

* Ensure API is running on port 8000
* Check Docker network

---

###  Database connection error

* Verify `.env` credentials
* Ensure DB container is healthy

---

###  Port conflict

```bash
lsof -i :8000
kill -9 <PID>
```

---

###  Validation errors

* Expected due to fault injection
* Check logs for malformed data

---

##  Debug Commands

### Test API

```bash
curl http://localhost:8000/v1/market-data
```

---

### Check DB (PostgreSQL)

```bash
docker exec -it <container_id> psql -U postgres
```

---

### View ETL Logs

```bash
docker-compose logs -f etl
```

---

##  Summary

This system demonstrates:

* Fault-tolerant data ingestion
* Data validation & quality control
* Scalable ETL architecture
* Containerized deployment

---

System Design Questions

1. Scaling for 1 Billion Events per Day
To scale for ~12,000 events per second (1 billion/day):

Ingestion Layer: Replace the polling ETL with a message broker like Apache Kafka or AWS Kinesis. The API would push events to a "raw-data" topic.
Processing Layer: Use distributed streaming frameworks like Apache Spark Streaming or Apache Flink to consume from Kafka and perform windowed transformations (VWAP).
Storage: Move from a single relational DB to a Data Lake (S3/GCS) for raw storage and a high-performance NoSQL/OLAP database (like ClickHouse, Druid, or Cassandra) for queryable processed data.
Compute: Deploy the processing jobs on a Kubernetes cluster (EKS/GKE) for elastic scaling.


2. Monitoring
Health Checks:
API: /health or endpoint verification (already in docker-compose).
ETL: Use a heartbeat mechanism or push metrics to a gateway.
Metrics & Tools:
Use Prometheus to collect metrics like records_processed, error_rate, and latency.
Use Grafana for visualization.
Implement alerts (e.g., PagerDuty) if the pipeline lag increases or success rate drops.


3. Recovery / Idempotency
Idempotency: The use of a composite Primary Key (instrument_id, timestamp) with ON CONFLICT DO NOTHING ensures that if a batch is partially processed and retried, duplicates are not created.
Checkpointing: In a streaming system, Kafka consumer offsets ensure we resume from the last successfully acknowledged record.
Atomic Transactions: Use database transactions for batch inserts to ensure either all records in a batch are committed or none are (all-or-nothing).
