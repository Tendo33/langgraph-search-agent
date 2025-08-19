# LangGraph Search Agent - System Architecture Design

## Executive Summary

This document outlines the current architecture and proposed improvements for the LangGraph Search Agent, a sophisticated web research system that leverages Google Gemini models and Search API to conduct iterative, multi-loop research with proper citation management.

## 1. Current Architecture Analysis

### 1.1 System Overview

The LangGraph Search Agent is a state-based research system that follows a four-phase workflow:

```
[User Query] → Generate Queries → Web Research → Reflection → Evaluate → Finalize Answer
                                     ↑                               ↓
                                     ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

### 1.2 Core Components

#### 1.2.1 Graph Architecture
- **State Management**: LangGraph-based state machine with multiple state types
- **Node Types**: 4 primary nodes (generate_query, web_research, reflection, finalize_answer)
- **Flow Control**: Conditional routing based on research sufficiency and loop limits

#### 1.2.2 Data Models
- **OverallState**: Main state container with message history and research data
- **QueryGenerationState**: State for query generation phase
- **WebSearchState**: State for individual web searches
- **ReflectionState**: State for research evaluation and gap analysis

#### 1.2.3 External Dependencies
- **Google Gemini API**: For query generation, reflection, and answer synthesis
- **Google Search API**: For web search execution
- **FastAPI**: For REST API interface
- **Pydantic**: For data validation and serialization

### 1.3 Current Limitations

1. **Scalability**: Single-threaded execution limits parallel processing
2. **Error Handling**: Limited retry mechanisms and fallback strategies
3. **Caching**: No caching layer for repeated queries or results
4. **Monitoring**: Basic logging without comprehensive observability
5. **Configuration**: Static configuration without dynamic adjustment
6. **Security**: Basic API key management without rotation

## 2. Enhanced Architecture Design

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced LangGraph Search Agent              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   API Gateway   │    │  Load Balancer  │    │  Monitoring │ │
│  │  (FastAPI)      │────│   (HAProxy)     │────│   (Prometheus) │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                        │                        │ │
│           ▼                        ▼                        ▼ │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Rate Limiter  │    │   Auth Service  │    │   Logging   │ │
│  │  (Redis)        │    │   (JWT/OAuth)   │    │   (ELK)     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                        │                        │ │
│           ▼                        ▼                        ▼ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Worker Pool                                │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │  │  Worker 1   │ │  Worker 2   │ │  Worker 3   │ │  ...    │ │ │
│  │  │  (Research) │ │  (Research) │ │  (Research) │ │         │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                        │                        │ │
│           ▼                        ▼                        ▼ │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Cache Layer   │    │   Database      │    │   Message    │ │
│  │   (Redis)       │    │   (PostgreSQL)  │    │   Queue     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                        │                        │ │
│           ▼                        ▼                        ▼ │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   External APIs │    │   Configuration │    │   File       │ │
│  │   (Gemini/Search)│    │   Service      │    │   Storage   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Components

#### 2.2.1 API Gateway
- **Purpose**: Central entry point for all requests
- **Features**: Rate limiting, authentication, request routing
- **Implementation**: FastAPI with middleware plugins

#### 2.2.2 Worker Pool
- **Purpose**: Parallel execution of research tasks
- **Features**: Dynamic scaling, load balancing, fault tolerance
- **Implementation**: Celery with Redis broker

#### 2.2.3 Caching Layer
- **Purpose**: Reduce API calls and improve response times
- **Features**: Query result caching, session management
- **Implementation**: Redis with TTL policies

#### 2.2.4 Monitoring & Observability
- **Purpose**: System health monitoring and performance tracking
- **Features**: Metrics collection, alerting, log aggregation
- **Implementation**: Prometheus + Grafana + ELK stack

#### 2.2.5 Configuration Service
- **Purpose**: Centralized configuration management
- **Features**: Dynamic updates, environment-specific settings
- **Implementation**: Consul or etcd

## 3. API Interface Design

### 3.1 REST API Endpoints

#### 3.1.1 Research Endpoints

```python
# Primary research endpoint
POST /api/v1/research
{
    "question": "What are the latest developments in AI?",
    "max_research_loops": 3,
    "initial_search_query_count": 5,
    "reasoning_model": "gemini-2.5-pro",
    "priority": "normal",
    "callback_url": "https://example.com/callback"
}

# Async research status
GET /api/v1/research/{research_id}/status
{
    "status": "completed|in_progress|failed",
    "progress": 85,
    "estimated_completion": "2024-01-15T14:30:00Z",
    "current_phase": "reflection"
}

# Research results
GET /api/v1/research/{research_id}/results
{
    "answer": "Comprehensive research answer...",
    "sources": [...],
    "metadata": {
        "research_loops": 3,
        "queries_executed": 12,
        "processing_time": 45.2,
        "model_used": "gemini-2.5-pro"
    }
}
```

#### 3.1.2 Management Endpoints

```python
# System health
GET /api/v1/health
{
    "status": "healthy",
    "version": "2.0.0",
    "components": {
        "database": "healthy",
        "cache": "healthy",
        "external_apis": "healthy"
    }
}

# Configuration management
GET /api/v1/config
PUT /api/v1/config
{
    "query_generator_model": "gemini-2.5-flash",
    "max_research_loops": 3,
    "rate_limits": {
        "requests_per_minute": 60,
        "concurrent_requests": 10
    }
}

# Usage statistics
GET /api/v1/stats
{
    "total_requests": 1250,
    "avg_processing_time": 42.5,
    "success_rate": 98.2,
    "popular_queries": [...]
}
```

### 3.2 WebSocket Interface

```python
# Real-time research updates
ws://localhost:8000/ws/research/{research_id}

# Message format
{
    "type": "progress_update|phase_change|error|completion",
    "timestamp": "2024-01-15T14:25:30Z",
    "data": {
        "phase": "web_research",
        "progress": 60,
        "current_query": "AI developments 2024",
        "sources_found": 8
    }
}
```

## 4. Component Interface Design

### 4.1 Research Engine Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ResearchRequest:
    question: str
    max_loops: int = 2
    initial_queries: int = 3
    reasoning_model: str = "gemini-2.5-pro"
    priority: str = "normal"
    callback_url: Optional[str] = None

@dataclass
class ResearchResult:
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class ResearchEngine(ABC):
    @abstractmethod
    async def start_research(self, request: ResearchRequest) -> str:
        """Start research task and return task ID"""
        pass
    
    @abstractmethod
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get research task status"""
        pass
    
    @abstractmethod
    async def get_results(self, task_id: str) -> Optional[ResearchResult]:
        """Get research results"""
        pass
    
    @abstractmethod
    async def cancel_research(self, task_id: str) -> bool:
        """Cancel ongoing research"""
        pass
```

### 4.2 Cache Interface

```python
from typing import Any, Optional
import asyncio

class CacheInterface(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
```

### 4.3 Monitoring Interface

```python
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_requests: int
    queue_size: int
    api_latency: float
    error_rate: float

class MonitoringInterface(ABC):
    @abstractmethod
    async def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric"""
        pass
    
    @abstractmethod
    async def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter"""
        pass
    
    @abstractmethod
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        pass
    
    @abstractmethod
    async def create_alert(self, name: str, condition: str, message: str):
        """Create an alert"""
        pass
```

## 5. Data Models and Schemas

### 5.1 Enhanced Data Models

```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ResearchStatus(str, Enum):
    PENDING = "pending"
    QUERY_GENERATION = "query_generation"
    WEB_RESEARCH = "web_research"
    REFLECTION = "reflection"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ResearchTask(BaseModel):
    id: str = Field(..., description="Unique task identifier")
    question: str = Field(..., description="Research question")
    status: ResearchStatus = Field(default=ResearchStatus.PENDING)
    priority: Priority = Field(default=Priority.NORMAL)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None
    current_phase: Optional[str] = None
    error_message: Optional[str] = None
    callback_url: Optional[str] = None
    
    class Config:
        use_enum_values = True

class QueryResult(BaseModel):
    query: str = Field(..., description="Search query executed")
    results: List[str] = Field(default_factory=list)
    sources: List[Dict[str, str]] = Field(default_factory=list)
    execution_time: float = Field(..., description="Query execution time in seconds")
    success: bool = Field(default=True)
    error_message: Optional[str] = None

class ResearchSession(BaseModel):
    id: str = Field(..., description="Session identifier")
    task_id: str = Field(..., description="Associated task ID")
    initial_queries: List[QueryResult] = Field(default_factory=list)
    follow_up_queries: List[QueryResult] = Field(default_factory=list)
    reflection_results: List[Dict[str, Any]] = Field(default_factory=list)
    final_answer: Optional[str] = None
    all_sources: List[Dict[str, str]] = Field(default_factory=list)
    total_processing_time: float = Field(default=0.0)
    research_loops: int = Field(default=0)
    model_used: str = Field(default="gemini-2.5-flash")
    
    class Config:
        use_enum_values = True

class SystemConfiguration(BaseModel):
    query_generator_model: str = Field(default="gemini-2.5-flash")
    reflection_model: str = Field(default="gemini-2.5-flash")
    answer_model: str = Field(default="gemini-2.5-pro")
    max_initial_queries: int = Field(default=5, ge=1, le=10)
    max_research_loops: int = Field(default=3, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)
    rate_limits: Dict[str, int] = Field(
        default_factory=lambda: {
            "requests_per_minute": 60,
            "concurrent_requests": 10,
            "queries_per_second": 5
        }
    )
    cache_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "ttl_seconds": 3600,
            "max_size": 1000
        }
    )
    
    class Config:
        use_enum_values = True
```

### 5.2 Event Schemas

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResearchEvent:
    event_type: str
    task_id: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class SystemEvent:
    event_type: str
    timestamp: datetime
    component: str
    severity: str
    message: str
    metadata: Dict[str, Any]
```

## 6. Implementation Roadmap

### 6.1 Phase 1: Core Enhancements (4-6 weeks)
- [ ] Implement async/await patterns throughout the codebase
- [ ] Add comprehensive error handling and retry mechanisms
- [ ] Implement basic caching layer with Redis
- [ ] Add logging and basic monitoring
- [ ] Enhance configuration management

### 6.2 Phase 2: Scalability Improvements (6-8 weeks)
- [ ] Implement worker pool with Celery
- [ ] Add database layer for persistence
- [ ] Implement rate limiting and authentication
- [ ] Add WebSocket support for real-time updates
- [ ] Implement proper API versioning

### 6.3 Phase 3: Advanced Features (8-10 weeks)
- [ ] Add machine learning for query optimization
- [ ] Implement advanced caching strategies
- [ ] Add comprehensive monitoring and alerting
- [ ] Implement A/B testing framework
- [ ] Add multi-tenant support

### 6.4 Phase 4: Production Readiness (4-6 weeks)
- [ ] Load testing and performance optimization
- [ ] Security audit and hardening
- [ ] Documentation and API reference
- [ ] Deployment automation and CI/CD
- [ ] Backup and disaster recovery

## 7. Security Considerations

### 7.1 Authentication & Authorization
- **API Keys**: Secure API key management with rotation
- **JWT Tokens**: For user authentication
- **OAuth2 Integration**: For third-party access
- **Role-Based Access Control**: For different user types

### 7.2 Data Protection
- **Encryption**: At rest and in transit
- **Data Masking**: For sensitive information
- **Audit Logging**: For compliance and security
- **Rate Limiting**: To prevent abuse

### 7.3 API Security
- **Input Validation**: To prevent injection attacks
- **Output Sanitization**: To prevent data leakage
- **CORS Protection**: For web applications
- **DDoS Protection**: With rate limiting and monitoring

## 8. Performance Requirements

### 8.1 Response Times
- **Simple Query**: < 30 seconds
- **Complex Research**: < 5 minutes
- **API Response**: < 100ms for status checks
- **Cache Hit**: < 10ms

### 8.2 Scalability Targets
- **Concurrent Users**: 1000+
- **Requests per Second**: 100+
- **Database Connections**: 50+
- **Cache Hit Rate**: > 80%

### 8.3 Availability Requirements
- **Uptime**: 99.9%
- **Response Time**: < 1s for 95% of requests
- **Error Rate**: < 1%
- **Recovery Time**: < 5 minutes

## 9. Monitoring & Observability

### 9.1 Key Metrics
- **Request Volume**: Total requests per time period
- **Response Times**: P50, P90, P99 percentiles
- **Error Rates**: By type and endpoint
- **Resource Usage**: CPU, memory, disk, network
- **API Performance**: Latency and success rates
- **Cache Performance**: Hit rates and efficiency

### 9.2 Alerting Thresholds
- **High Error Rate**: > 5% for 5 minutes
- **Slow Response**: P99 > 2 seconds for 5 minutes
- **High Memory Usage**: > 80% for 10 minutes
- **API Failures**: > 10% failure rate for 2 minutes
- **Cache Issues**: Hit rate < 70% for 10 minutes

## 10. Conclusion

The enhanced LangGraph Search Agent architecture provides a robust, scalable, and maintainable foundation for advanced web research capabilities. By implementing the proposed improvements, the system will be able to handle increased load, provide better user experience, and offer enhanced monitoring and debugging capabilities.

The design emphasizes modularity, scalability, and maintainability while preserving the core functionality of the original system. The phased implementation approach allows for gradual improvement while maintaining system availability.

---

*This design document should be reviewed and updated as the project progresses and requirements evolve.*