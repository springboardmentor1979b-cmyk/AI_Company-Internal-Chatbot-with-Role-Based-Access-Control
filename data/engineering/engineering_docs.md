# Engineering Department Documentation — 2024

## System Architecture Overview
The platform is built on a microservices architecture deployed on AWS infrastructure.

### Technology Stack
- Backend: Python 3.11, FastAPI, SQLAlchemy
- Frontend: React 18, TypeScript, TailwindCSS
- Database: PostgreSQL 15 (primary), Redis 7 (cache)
- Vector Store: ChromaDB with all-MiniLM-L6-v2 embeddings
- LLM: TinyLlama 1.1B (on-premise), GPT-4 (fallback)
- Infrastructure: AWS ECS, RDS, ElastiCache, CloudFront
- CI/CD: GitHub Actions, Docker, Kubernetes

## Team Structure
- Total engineers: 42
- Frontend team: 10 engineers
- Backend team: 14 engineers
- DevOps/Cloud: 6 engineers
- ML/AI team: 8 engineers
- QA team: 4 engineers

## Sprint Metrics (Q4 2024)
- Average velocity: 84 story points per sprint
- Bug resolution time: 2.3 days average
- Code review turnaround: 4 hours average
- Deployment frequency: 2.4 times per week
- Mean time to recovery (MTTR): 47 minutes
- System uptime: 99.94%

## Infrastructure & Costs
- Monthly AWS bill: ₹18,40,000
- Cost per user: ₹42/month
- Storage used: 48 TB
- Peak concurrent users: 12,400
- API response time p99: 340ms

## Security & Compliance
- All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- RBAC implemented at API and database layer
- Penetration testing conducted quarterly
- SOC 2 Type II certification: In progress
- VAPT completed: August 2024 — 0 critical, 3 medium (resolved)
- Access logs retained for 90 days

## Q4 2024 Deliverables
- ✅ RBAC Intelligence Platform v2.0 launched
- ✅ Vector search latency reduced by 40%
- ✅ Mobile app v3.2 released (iOS + Android)
- ✅ API gateway migration completed
- 🔄 GraphQL API layer (in progress — 70% complete)
- 🔄 Multi-region deployment (planned Q1 2025)

## Engineering Budget FY2025
- Total approved: ₹4,80,00,000
- Salaries: 65% (₹3,12,00,000)
- Infrastructure: 20% (₹96,00,000)
- Tools & licenses: 10% (₹48,00,000)
- Training: 5% (₹24,00,000)

## Hiring Plan 2025
- 8 new backend engineers
- 4 ML engineers (LLM specialisation)
- 3 DevOps engineers
- 2 security engineers
