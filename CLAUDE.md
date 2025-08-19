# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph-based research agent API service that uses Google Gemini and Google Search for automated web research. The project implements a sophisticated multi-loop research workflow that generates search queries, performs web research, reflects on results, and finalizes comprehensive answers with proper citations.

## Common Commands

### Development Commands
```bash
# Install dependencies
make install
# or
pip install -e .

# Run the development server
make run
# or
python run_server.py

# Test the API
make test
# or
python examples/api_example.py

# Code formatting and linting
make format        # ruff format .
make lint          # ruff check .
make dev           # format + lint + run

# Clean up build artifacts
make clean
```

### Testing
```bash
# Run API integration tests
python examples/api_example.py

# Test the CLI interface
python examples/cli_research.py "What is the capital of France?"

# Test with custom parameters
python examples/cli_research.py "AI developments" --initial-queries=2 --max-loops=3 --reasoning-model=gemini-2.5-pro
```

## Architecture

### Core Components

**LangGraph Workflow (src/search_agent/graph.py)**:
- `generate_query`: Creates optimized search queries using Gemini 2.0 Flash
- `web_research`: Executes parallel web searches using Google Search API
- `reflection`: Analyzes results and identifies knowledge gaps
- `evaluate_research`: Determines if more research is needed
- `finalize_answer`: Generates comprehensive final answer with citations

**State Management (src/search_agent/state.py)**:
- `OverallState`: Main state tracking messages, queries, results, and loop counts
- `ReflectionState`: State for reflection analysis and follow-up query generation
- `WebSearchState`: State for individual web search operations
- `QueryGenerationState`: State for search query generation

**Configuration (src/search_agent/configuration.py)**:
- `Configuration`: Pydantic model for agent settings
- Environment variable support with fallback to defaults
- Configurable models: query_generator, reflection, answer

**API Layer (src/search_agent/app.py)**:
- FastAPI application with CORS middleware
- `/research` endpoint for research queries
- `/health` and `/config` endpoints for monitoring
- Automatic LangGraph graph initialization

### Key Dependencies

**Core Stack**:
- `langgraph>=0.2.6`: Graph-based agent orchestration
- `langchain>=0.3.19`: LLM framework integration
- `langchain-google-genai`: Google Gemini model integration
- `fastapi`: REST API framework
- `uvicorn`: ASGI server

**Research Tools**:
- `google-genai`: Direct Google API access for search with grounding
- `python-dotenv`: Environment variable management

### Research Workflow

1. **Query Generation**: Creates multiple diverse search queries based on the user's question
2. **Parallel Web Research**: Executes queries concurrently using Google Search API
3. **Citation Processing**: Extracts and formats citations with URL resolution
4. **Reflection Analysis**: Identifies knowledge gaps and generates follow-up queries
5. **Loop Evaluation**: Decides whether to continue research or finalize answer
6. **Answer Finalization**: Generates comprehensive answer with proper source citations

### Configuration Options

**Environment Variables**:
- `GEMINI_API_KEY`: Required for Google Gemini API access
- `GOOGLE_SEARCH_API_KEY`: Required for Google Search API access

**Configurable Parameters**:
- `query_generator_model`: Model for query generation (default: gemini-2.5-flash)
- `reflection_model`: Model for reflection analysis (default: gemini-2.5-flash)
- `answer_model`: Model for final answer (default: gemini-2.5-pro)
- `number_of_initial_queries`: Initial search queries to generate (default: 3)
- `max_research_loops`: Maximum research iterations (default: 2)

## Important Implementation Details

### Citation System
The project implements a sophisticated citation system that:
- Resolves long Google Search URLs to short, unique identifiers
- Inserts citation markers directly into generated text
- Maintains source tracking throughout the research process
- Formats citations as markdown links in final answers

### Parallel Processing
The LangGraph workflow supports parallel execution:
- Multiple search queries run concurrently
- Follow-up queries from reflection phase execute in parallel
- Efficient resource utilization with proper state management

### Error Handling
- Graceful degradation when API keys are missing
- Comprehensive error responses from API endpoints
- Automatic graph initialization with fallback handling

### Code Style
The project uses `ruff` for linting and formatting with specific rules:
- Google docstring convention
- Type hints throughout the codebase
- Structured output parsing with Pydantic models
- Proper error handling and logging

## Testing and Development

### API Testing
Use `examples/api_example.py` to test all API endpoints:
- Health check endpoint
- Configuration endpoint
- Research endpoint with sample queries

### CLI Testing
Use `examples/cli_research.py` for direct command-line testing:
- Simple research queries
- Custom parameter testing
- Performance evaluation

### Development Server
The development server runs on `http://localhost:8000` with:
- Interactive API documentation at `/docs`
- Alternative documentation at `/redoc`
- CORS support for web application integration