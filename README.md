 End-to-End Data Engineering & Infrastructure Project

 Overview

This project demonstrates a complete **data engineering pipeline** that simulates real-time market data ingestion, processing, validation, and storage using modern tools and best practices.

The system is designed to be:

* **Scalable**
* **Resilient (Fault-tolerant)**
* **Containerized (Docker-based)**
* **Production-ready**

---

 Architecture

The solution consists of three main components:

 1. Source API (FastAPI)

* Simulates real-time financial market data
* Provides endpoint: `/v1/market-data`
* Includes **fault injection (5%)** to test pipeline resilience

2. ETL Pipeline (Python)

* Extracts data from API
* Validates using **Pydantic**
* Performs transformations:

  * VWAP calculation
  * Outlier detection
* Loads cleaned data into PostgreSQL

3. Sink (PostgreSQL)

* Stores processed, validated, and deduplicated data
* Ensures **data integrity using primary keys**

---

## Data Flow

```
FastAPI → ETL Pipeline → PostgreSQL
```

1. API generates synthetic data
2. ETL fetches and validates data
3. Applies business logic (VWAP, outliers)
4. Stores clean data in DB

---

 Features

*  Fault-tolerant API (Chaos Engineering)
*  Schema validation using Pydantic
* zVWAP (Volume Weighted Average Price)
* Outlier detection (±15%)
*  Duplicate prevention (Primary Key)
*  Structured logging
*  Fully Dockerized setup

---

##  Project Structure

```
data-engineering/
│
├── api/                # FastAPI service
├── etl/                # ETL pipeline
├── docker-compose.yml  # Orchestration
├── .env                # Environment variables
├── README.md
```

---

##  How to Run the Project

###  Step 1: Clone Repository

```bash
git clone https://github.com/chekuritharun/data-engineering.git
cd data-engineering
```

---

###  Step 2: Setup Environment Variables

Create a `.env` file:

```env
DB_NAME=market
DB_USER=postgres
DB_PASS=postgres
```

---

### Step 3: Run Docker Containers

```bash
docker-compose up --build
```

This will start:

* API → http://localhost:8000
* PostgreSQL → port 5432
* ETL pipeline → runs automatically

---

###  Step 4: Create Database Table

Connect to PostgreSQL and run:

```sql
CREATE TABLE market_data (
    instrument_id TEXT,
    price FLOAT,
    volume FLOAT,
    timestamp TIMESTAMP,
    PRIMARY KEY (instrument_id, timestamp)
);
```

---

###  Step 5: Test API

```bash
curl http://localhost:8000/v1/market-data
```

---

##  ETL Logic Explained

###  Extraction

* Polls API every 10 seconds
* Handles:

  * Timeouts
  * API failures (500 errors)

---

###  Validation

* Uses **Pydantic**
* Drops invalid records

---

###  Transformation

#### 1. VWAP Calculation

```
VWAP = Σ(price × volume) / Σ(volume)
```

#### 2. Outlier Detection

* Drops records where:

```
|price - avg_price| > 15%
```

---

###  Loading

* Inserts into PostgreSQL
* Uses:

```sql
ON CONFLICT DO NOTHING
```

→ Prevents duplicates

---

##  Logging

Tracks:

* Total records processed
* Dropped records
* Errors
* Execution time

---

##  System Design Answers

###  1. Scaling (1 Billion Events/day)

To scale:

* Use **Kafka** for ingestion
* Use **Spark/Flink** for processing
* Store in **Data Lake (S3/ADLS)**
* Deploy on **Kubernetes**
* Use **Delta Lake / Iceberg**

---

###  2. Monitoring

Implement:

* Health check endpoint (`/health`)
* Prometheus + Grafana
* Centralized logging (ELK stack)

Monitor:

* API latency
* ETL failures
* Data drops

---

###  3. Recovery & Idempotency

Ensured using:

* Primary key (instrument_id + timestamp)
* UPSERT (`ON CONFLICT DO NOTHING`)
* Checkpointing
* Safe reprocessing

---

##  Future Improvements

* Add **Kafka streaming pipeline**
* Use **Apache Airflow** for orchestration
* Deploy on **AWS/Azure**
* Add **CI/CD pipeline**
* Implement **data partitioning**

---

##  Key Learnings

* Building fault-tolerant pipelines
* Data validation and quality control
* Real-time ingestion concepts
* Docker-based deployment
* Production-ready system design

---







 
