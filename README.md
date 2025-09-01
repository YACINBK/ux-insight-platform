# UX Insight Platform

A production-ready, containerized platform for UX analysis and reporting. This platform combines Spring Boot orchestration with FastAPI LLM and Vision services, featuring an Angular frontend with provider-agnostic LLM integration.

## 🚀 Features

- **Multi-Service Architecture**: Spring Boot gateway orchestrates FastAPI LLM and Vision services
- **Provider-Agnostic LLM**: Support for OpenAI, Mistral, DeepSeek, OpenRouter, and local Ollama
- **Vision Analysis**: OCR and image analysis capabilities
- **Modern Frontend**: Angular application with Material Design
- **Containerized**: Docker Compose setup for easy deployment
- **RAG Integration**: ChromaDB-based vector search and retrieval
- **Production Ready**: Environment-driven configuration and proper service separation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular       │    │   Spring Boot   │    │   FastAPI LLM   │
│   Frontend      │◄──►│   Gateway       │◄──►│   Service       │
│   (Port 4200)   │    │   (Port 8080)   │    │   (Port 5000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   FastAPI       │
                       │   Database      │    │   Vision        │
                       │   (Port 5432)   │    │   (Port 5001)   │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- API keys for your chosen LLM provider (optional for local Ollama)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/YACINBK/ux-insight-platform.git
   cd ux-insight-platform
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

3. **Start the platform**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:4200
   - Spring Boot API: http://localhost:8080
   - FastAPI LLM: http://localhost:5000
   - FastAPI Vision: http://localhost:5001

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
POSTGRES_DB=uxdb
POSTGRES_USER=uxuser
POSTGRES_PASSWORD=uxpass

# Frontend Configuration
FRONTEND_ORIGIN=http://localhost:4200

# LLM Provider Configuration
LLM_PROVIDER=openai  # openai, mistral, deepseek, openrouter, ollama
OPENAI_API_KEY=your_openai_key
MISTRAL_API_KEY=your_mistral_key
DEEPSEEK_API_KEY=your_deepseek_key
OPENROUTER_API_KEY=your_openrouter_key

# Ollama Configuration (for local models)
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

# Service Ports
SPRINGBOOT_PORT=8080
LLM_API_PORT=5000
VISION_API_PORT=5001
```

### LLM Provider Setup

#### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
```

#### Mistral
```env
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_mistral_api_key
```

#### DeepSeek
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
```

#### OpenRouter
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
```

#### Local Ollama
```env
LLM_PROVIDER=ollama
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b
```

## 📁 Project Structure

```
ux-insight-platform/
├── .env                    # Environment variables
├── .env.example           # Environment template
├── docker-compose.yml     # Multi-service orchestration
├── README.md              # This file
├── backend/               # Backend services
│   ├── springboot/        # Spring Boot gateway
│   │   └── ux_beta/
│   │       ├── src/main/java/com/example/ux_beta/
│   │       │   ├── controller/     # REST controllers
│   │       │   ├── service/        # Business logic
│   │       │   ├── repository/     # Data access
│   │       │   ├── domain/         # Entity models
│   │       │   ├── dto/            # Data transfer objects
│   │       │   └── config/         # Configuration
│   │       └── Dockerfile
│   ├── fastapi_llm/       # LLM API service
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── fastapi_vision/    # Vision/OCR service
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── postgres/          # Database setup
│       ├── init.sql
│       └── data/
├── frontend/              # Angular application
│   ├── src/app/
│   │   ├── components/    # Angular components
│   │   ├── services/      # Angular services
│   │   └── ...
│   ├── public/
│   │   └── env.js         # Runtime environment config
│   ├── nginx.conf         # Nginx configuration
│   └── Dockerfile
├── datasets/              # Dataset configurations
├── infra/                 # Infrastructure configs
├── packages/              # Third-party packages
└── scripts/               # Utility scripts
```

## 🛠️ Development

### Running Locally

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

### Building Individual Services

```bash
# Build frontend only
docker-compose build frontend

# Build Spring Boot only
docker-compose build springboot-gateway

# Build FastAPI services
docker-compose build fastapi-llm fastapi-vision
```

## 🔍 API Endpoints

### Spring Boot Gateway (Port 8080)

- `GET /api/questions` - Get all questions
- `POST /api/questions` - Submit a new question
- `GET /api/questions/dashboard/stats` - Get dashboard statistics
- `POST /api/llm/query` - Query LLM service
- `POST /api/questions/vision/analyze` - Analyze images
- `POST /api/questions/premium-auto/analyze` - Premium auto analysis

### FastAPI LLM Service (Port 5000)

- `POST /query` - Query LLM with RAG
- `GET /health` - Health check

### FastAPI Vision Service (Port 5001)

- `POST /analyze` - Analyze images
- `GET /health` - Health check

## 🧪 Testing

The platform includes comprehensive testing capabilities:

- **Unit Tests**: Individual service tests
- **Integration Tests**: Service-to-service communication
- **End-to-End Tests**: Full user workflow testing

## 📊 Monitoring

- **Health Checks**: Built into all services
- **Logging**: Structured logging across all services
- **Metrics**: Performance monitoring capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## 🔄 Updates

Stay updated with the latest features and improvements by:
- Watching the repository
- Checking the releases page
- Following the changelog

---

**Built with ❤️ for the UX community**

