# ClientNest 🏢

> **AI-Powered Client Relationship Management Platform**

ClientNest is a comprehensive CRM solution that leverages artificial intelligence to transform how businesses manage client relationships, automate workflows, and drive growth through intelligent insights.

## ⭐️ Overview

ClientNest combines traditional CRM functionality with cutting-edge AI capabilities to provide:

- **Intelligent Client Management**: AI-powered client profiling and relationship tracking
- **Automated Workflows**: Smart automation for routine tasks and follow-ups
- **Predictive Analytics**: Data-driven insights for sales forecasting and client behavior
- **Multi-Channel Communication**: Unified communication across email, chat, and social media
- **Advanced Reporting**: Real-time dashboards and customizable analytics
- **Scalable Architecture**: Designed for future mobile development with modular components
- **Personalized Recommendations**: Integrated recommendation system powered by a dedicated ML microservice

## 🧠 Recommendation System & ML Service

ClientNest includes a robust recommendation system and a dedicated ML microservice:
- **Recommendation System**: Delivers personalized content and churn predictions, integrated with the Django backend.
- **ML Service**: FastAPI-based microservice providing collaborative, content-based, and hybrid recommendations, as well as churn prediction APIs.
- **Integration**: The backend communicates with the ML service via HTTP for real-time recommendations and analytics.

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)
- **Docker** and Docker Compose
- **Git**
- **AWS CLI** (for cloud deployment)

### Local Development Setup (Non-Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/zentrix-innovative-labs/client-nest.git
   cd client-nest
   ```
2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv  # Or use python -m venv .venv for consistency
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Copy the example env file and edit as needed
   # Edit .env with your configuration (see below for required variables)
   python manage.py migrate
   python manage.py runserver
   ```

#### Required Environment Variables
The backend requires a `.env` file in the `backend/` directory. You can copy `backend/.env.example` and fill in your values. The following variables are required:

| Variable              | Description                                 |
|-----------------------|---------------------------------------------|
| DJANGO_SECRET_KEY     | Django secret key (required)                |
| POSTGRES_DB           | Postgres database name                      |
| POSTGRES_USER         | Postgres username                           |
| POSTGRES_PASSWORD     | Postgres password                           |
| POSTGRES_HOST         | Postgres host (default: localhost)          |
| POSTGRES_PORT         | Postgres port (default: 5432)               |
| EMAIL_HOST            | SMTP server host                            |
| EMAIL_PORT            | SMTP server port                            |
| EMAIL_USE_TLS         | Use TLS for email (True/False)              |
| EMAIL_USE_SSL         | Use SSL for email (True/False)              |
| EMAIL_HOST_USER       | SMTP username                               |
| EMAIL_HOST_PASSWORD   | SMTP password                               |
| DEFAULT_FROM_EMAIL    | Default from email address                  |
| FACEBOOK_APP_ID       | Facebook App ID (optional)                  |
| FACEBOOK_APP_SECRET   | Facebook App Secret (optional)              |
| FACEBOOK_REDIRECT_URI | Facebook Redirect URI (optional)            |

3. **Frontend Setup**
   ```bash
   # The frontend directory is not present in this repository. If/when it is added, follow the instructions in that directory.
   ```
4. **Database Setup**
   ```bash
   docker-compose up -d db redis
   # (Now uses PostgreSQL 14 by default)
   ```
5. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Dockerized Development (Recommended)
### Docker Development

> **Note:** If you wish to use Docker Compose for Postgres/Redis, ensure a `docker-compose.yml` file is present. If not, you must install and run Postgres and Redis manually.

```bash
# Start all services (backend, ML service, db, redis)
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

- The backend will be available at `http://localhost:8000`
- The ML service will be available at `http://localhost:8001`
- PostgreSQL 14 and Redis are started automatically

## 📦 Project Structure

```
clientnest/
├── 📄 README.md
├── 🔒 .gitignore
├── 📋 product-research/          # Market analysis and requirements
│   ├── 00-executive-summary.md
│   ├── 01-market-analysis.md
│   ├── 02-feature-specifications.md
│   ├── 03-pricing-strategy.md
│   ├── 04-technical-requirements.md
│   ├── 05-ux-design-requirements.md
│   └── 06-ai-integration-requirements.md
├── 🏗️ system-architecture/       # Technical architecture docs
│   ├── 01-system-overview.md
│   ├── 02-technology-stack.md
│   ├── 03-high-level-architecture.md
│   ├── 04-database-design.md
│   ├── 05-api-design.md
│   ├── 06-frontend-architecture.md
│   ├── 07-security-architecture.md
│   ├── 08-ai-integration-architecture.md
│   ├── 09-data-science-architecture.md
│   ├── 10-team-specific-guides.md
│   ├── 11-implementation-guide.md
│   └── 12-architecture-summary.md
└── 👥 team-task-distribution/    # Team member task assignments
    ├── ai-team/                 # AI team member tasks
    ├── backend/                 # Backend team member tasks
    ├── cloud/                   # Cloud team member tasks
    ├── data-science/            # Data science team member tasks
    ├── frontend/                # Frontend team member tasks
    └── security/                # Security team member tasks
```

## 👥 Team Structure

Our development team is organized into specialized groups with detailed task assignments:

### 🔧 Backend Team
- **[Mukiisa Mark](./team-task-distribution/backend/mukiisa-mark.md)** - Senior Backend Developer & Team Lead
- **[Atim Carol](./team-task-distribution/backend/atim-carol.md)** - Backend Developer

### 🎨 Frontend Team
- **[Miriam Birungi](./team-task-distribution/frontend/miriam-birungi.md)** - Senior Frontend Developer & Team Mentor
- **[Nshabohurira Connie](./team-task-distribution/frontend/nshabohurira-connie.md)** - Frontend Developer
- **[Mugisha Jovan](./team-task-distribution/frontend/mugisha-jovan.md)** - Frontend Developer

### 🤖 AI Team
- **[Onyait Elias](./team-task-distribution/ai-team/onyait-elias.md)** - AI Engineer & Team Lead
- **[Buwembo Denzel](./team-task-distribution/ai-team/buwembo-denzel.md)** - AI Content Specialist
- **[Biyo Stella](./team-task-distribution/ai-team/biyo-stella.md)** - AI Quality Assurance Specialist

### 📊 Data Science Team
- **[Yolamu Timothy](./team-task-distribution/data-science/yolamu-timothy.md)** - Data Analytics Lead & Mentor
- **[Apunyo Mark](./team-task-distribution/data-science/apunyo-mark.md)** - Data Science Specialist
- **[Nabukera Remmy](./team-task-distribution/data-science/nabukera-remmy.md)** - Junior Data Analyst

### 🔐 Security Team
- **[Twinamastiko Brinton](./team-task-distribution/security/twinamastiko-brinton.md)** - Security Specialist
- **[Odoi Imma](./team-task-distribution/security/odoi-imma.md)** - Security Engineer
- **[Stuart](./team-task-distribution/security/stuart.md)** - Security Analyst & Compliance Specialist

### ☁️ Cloud Team
- **[Edwin](./team-task-distribution/cloud/edwin.md)** - Cloud Infrastructure Engineer

## 🔄 Development Workflow

### Git Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/your-feature-name
   # Make your changes
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

2. **Pull Request Process**
   - Create PR with detailed description
   - Request review from team lead
   - Ensure all tests pass
   - Merge after approval

### Code Standards

**Python (Backend)**
- Follow PEP 8 style guide
- Use Black for code formatting
- Type hints required
- Docstrings for all functions

**JavaScript/TypeScript (Frontend)**
- ESLint and Prettier configuration
- TypeScript strict mode
- Component documentation
- Unit tests for utilities

**Commit Messages**
- Use conventional commits format
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Example: `feat(auth): add OAuth2 integration`

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End Testing
```bash
npm run test:e2e
```

## 🚀 Deployment

### Development Environment
- **URL**: https://dev.clientnest.com
- **Auto-deploy**: On push to `develop` branch

### Staging Environment
- **URL**: https://staging.clientnest.com
- **Deploy**: Manual trigger from `develop` branch

### Production Environment
- **URL**: https://app.clientnest.com
- **Deploy**: Manual trigger from `main` branch
- **Requires**: Code review and QA approval

### Infrastructure

```bash
# Deploy infrastructure
cd infrastructure
terraform init
terraform plan
terraform apply

# Deploy application
./scripts/deploy.sh production
```

## 🔐 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- OAuth2 integration (Google, Microsoft)
- Session management and timeout

### Data Protection
- End-to-end encryption for sensitive data
- GDPR and CCPA compliance
- Regular security audits
- Automated vulnerability scanning
- Secure API endpoints with rate limiting

### Infrastructure Security
- AWS WAF for application protection
- VPC with private subnets
- Encrypted data at rest and in transit
- Regular backup and disaster recovery
- Security monitoring and alerting

## 📚 Documentation

### 📋 Available Documentation
- **[Product Research](./product-research/)** - Market analysis, feature specifications, and business requirements
  - [Executive Summary](./product-research/00-executive-summary.md)
  - [Market Analysis](./product-research/01-market-analysis.md)
  - [Feature Specifications](./product-research/02-feature-specifications.md)
  - [Pricing Strategy](./product-research/03-pricing-strategy.md)
  - [Technical Requirements](./product-research/04-technical-requirements.md)
  - [UX Design Requirements](./product-research/05-ux-design-requirements.md)
  - [AI Integration Requirements](./product-research/06-ai-integration-requirements.md)

- **[System Architecture](./system-architecture/)** - Technical architecture and design documentation
  - [System Overview](./system-architecture/01-system-overview.md)
  - [Technology Stack](./system-architecture/02-technology-stack.md)
  - [High-Level Architecture](./system-architecture/03-high-level-architecture.md)
  - [Database Design](./system-architecture/04-database-design.md)
  - [API Design](./system-architecture/05-api-design.md)
  - [Frontend Architecture](./system-architecture/06-frontend-architecture.md)
  - [Security Architecture](./system-architecture/07-security-architecture.md)
  - [AI Integration Architecture](./system-architecture/08-ai-integration-architecture.md)
  - [Data Science Architecture](./system-architecture/09-data-science-architecture.md)
  - [Team-Specific Guides](./system-architecture/10-team-specific-guides.md)
  - [Implementation Guide](./system-architecture/11-implementation-guide.md)
  - [Architecture Summary](./system-architecture/12-architecture-summary.md)

- **[Team Task Distribution](./team-task-distribution/)** - Individual team member assignments and sprint planning
  - [AI Team Tasks](./team-task-distribution/ai-team/)
  - [Backend Team Tasks](./team-task-distribution/backend/)
  - [Cloud Team Tasks](./team-task-distribution/cloud/)
  - [Data Science Team Tasks](./team-task-distribution/data-science/)
  - [Frontend Team Tasks](./team-task-distribution/frontend/)
  - [Security Team Tasks](./team-task-distribution/security/)

### 🔮 Future Documentation (To Be Created)
- **API Documentation** - REST API reference (to be created by backend team)
- **User Guide** - End-user documentation (to be created by frontend team)
- **Developer Guide** - Development setup and guidelines (to be created by team leads)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Ensure all tests pass**
6. **Submit a pull request**

### Development Guidelines

- Follow the established code style
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Request code review before merging

## 📞 Support

### Development Team
- **Technical Issues**: Create GitHub issue
- **Architecture Questions**: Contact team leads
- **Security Concerns**: Email security@zentrix-labs.com

### Communication Channels
- **Daily Standups**: 9:00 AM EAT
- **Sprint Planning**: Bi-weekly Mondays
- **Code Reviews**: Ongoing via GitHub
- **Team Chat**: Slack workspace

## 📄 License

This project is proprietary software owned by Zentrix Innovative Labs. All rights reserved.

## 🔄 Changelog

### Version 1.0.0 (In Development)
- Initial project setup and documentation
- Team task distribution and sprint planning
- System architecture design
- Product research and market analysis
- Technology stack selection
- Development workflow establishment

---

**Built with ❤️ by the Zentrix Innovative Labs Team**

For more information, visit our [product research](./product-research/), [system architecture](./system-architecture/), or [team task distribution](./team-task-distribution/) documentation.