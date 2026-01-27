# DataPulse - A production-ready monitoring platform for data pipelines with automated health checks, anomaly detection, and real-time dashboards.

>> Table of Contents

Overview
Key Features
Architecture
Tech Stack
Quick Start
Deployment
API Documentation
Performance
Screenshots


# Overview
DataPulse solves a critical problem in data engineering: How do you monitor hundreds of data pipelines in real-time?
In production environments, data pipelines power everything from customer analytics to ML model training. When pipelines fail silently, businesses lose money. DataPulse provides:

> Centralized monitoring - All pipeline health in one dashboard
> Automated health checks - No manual checking needed
> Anomaly detection - Statistical analysis catches issues early
> Real-time alerts - Slack notifications when pipelines fail
> Historical analytics - Track performance trends over time

# Real-world use cases:

Monitor ETL jobs processing customer data
Track API integrations and data quality checks
Oversee ML pipeline health (training, inference, feature stores)
Ensure SLA compliance with historical uptime tracking


# Key Features
1. Automated Health Monitoring

Background workers check pipelines every 60 seconds
Concurrent health checks using asyncio (50+ simultaneous checks)
Tracks response time, status codes, and error messages
Configurable check intervals and timeouts per pipeline

2. Smart Anomaly Detection 

Statistical analysis using the Z-score method
Detects unusual response times (98.8% confidence)
Identifies error rate spikes automatically
Provides confidence levels and historical context

3. Real-Time Dashboard

Live status updates (auto-refresh every 5 seconds)
Color-coded health indicators (green/yellow/red)
Performance metrics at a glance
Detailed per-pipeline analytics

4. Performance Optimized

Redis caching for hot data (sub-50ms response times)
Async/await throughout for maximum concurrency
Database query optimization with proper indexing
Efficient time-series queries for historical data

5. Production Ready

Deployed on Render.com (free tier)
PostgreSQL for data persistence
Proper error handling and logging
Horizontal scalability (add more workers)


# Data Flow

User adds pipeline → Stored in PostgreSQL
Background worker → Checks pipeline every 60s
Health check results → Saved to database + cached in Redis
Anomaly detector → Analyzes metrics using Z-score
Dashboard → Polls API every 5s for updates
Alerts → Sent to Slack on failures


# Tech Stack
> Backend

FastAPI - Modern async Python web framework
SQLAlchemy 2.0 - Async ORM for database operations
PostgreSQL - Primary data store (Neon.tech free tier)
Redis - Caching layer (Upstash free tier)
Pydantic - Data validation and serialization

> Frontend

Vanilla JavaScript - No framework overhead
Tailwind CSS - Utility-first styling
Jinja2 - Server-side templates
HTML5 - Semantic markup

> Infrastructure

Render.com - PaaS deployment (free tier)
GitHub Actions - CI/CD pipeline
Upstash - Managed Redis
Neon.tech - Serverless PostgreSQL

> Key Libraries

httpx - Async HTTP client for health checks
asyncio - Concurrency and background tasks
Statistics - Anomaly detection algorithms


=> Quick Start
Prerequisites

Python 3.11+
Git

Local Development
bash
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/datapulse.git
cd datapulse

2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Set up environment variables
cp .env.example .env
> Edit .env with your configuration

5. Initialize database
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

6. Run the application
uvicorn app.main:app --reload

7. Open browser
Visit: http://localhost:8000
Add Your First Pipeline

Click "+ Add Pipeline"
Fill in details:

Name: Test API
URL: https://httpbin.org/status/200
Type: batch


Wait ~60 seconds for first health check
Watch it turn green!


# Performance
> Benchmarks

API Response Time: <50ms (cached), <200ms (database)
Concurrent Health Checks: 50+ simultaneous
Dashboard Refresh: 5-second auto-update
Database Queries: Optimized with indexing
Cache Hit Rate: ~80% for hot data

> Scalability

Horizontal scaling via worker containers
Database connection pooling
Async I/O throughout stack
Efficient time-series queries

> Code Quality

Type hints throughout
Async/await best practices
Proper error handling
Structured logging


# Screenshots
<img width="1919" height="875" alt="Screenshot 2026-01-18 181956" src="https://github.com/user-attachments/assets/5bc6772a-5460-48e6-b933-dcc19426b200" />
<img width="1878" height="861" alt="image" src="https://github.com/user-attachments/assets/edba104f-73da-4fa6-a76b-8d499aa1b564" />
<img width="1875" height="861" alt="image" src="https://github.com/user-attachments/assets/38129322-6435-443f-bdf0-47fc31fa1031" />
<img width="1889" height="865" alt="image" src="https://github.com/user-attachments/assets/324f91f7-2cca-4f0a-8805-9fb81efd3efa" />


# Future Enhancements

 Cost tracking per pipeline (AWS Cost Explorer integration)
 Advanced filtering (search, tags, teams)
 Custom alerting rules (threshold configuration)
 Dashboard widgets (customizable views)
 API authentication (API keys)
 Multi-region support (global deployments)
 ML-based predictions (failure forecasting)


> Contributing
Contributions welcome! Please read CONTRIBUTING.md first.

Fork the repository
Create feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open Pull Request


> Author
Priyanshi Rathore

GitHub: @priyanshiii7


# Acknowledgments

Built for demonstrating distributed systems knowledge
Inspired by real production monitoring needs
Uses modern Python async patterns throughout
Twitter: @yourhandle


<div align="center">
⭐ Star this repo if you find it useful!
Made with ❤️ and Python
</div>
