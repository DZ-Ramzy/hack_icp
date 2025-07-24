# ICP Prediction Market Platform

A comprehensive decentralized prediction market platform built on the Internet Computer Protocol (ICP) with advanced AI-powered market analysis capabilities.

## Overview

This platform combines decentralized prediction markets with sophisticated AI agents to provide users with intelligent market analysis, optimal trading recommendations, and comprehensive risk assessment. The system features a modern web interface backed by ICP canisters and an advanced agent pipeline for market intelligence.

## Architecture

### Frontend Application

- **Next.js** with TypeScript for modern web interface
- **TailwindCSS** for responsive styling and design system
- **AgentJS** for seamless ICP blockchain integration
- **Chart.js** for real-time price visualization and analytics
- **Wallet Integration** supporting Plug, Stoic, and Internet Identity

### Backend Infrastructure

- **Motoko Canisters** for decentralized smart contract logic
  - Market Canister: Market creation, AMM trading, liquidity management
  - User Canister: User profiles, XP system, leaderboard tracking
  - Insight Canister: AI-powered market analysis integration
- **LMSR Algorithm** for automated market making and price discovery
- **Decentralized Storage** for market data and user information

### AI Agent Pipeline

- **Multi-Agent Architecture** with specialized analysis phases
- **Real-Time Research** via Tavily API integration
- **Advanced Analytics** with Kelly Criterion optimization
- **Scenario Analysis** for comprehensive risk assessment
- **Memory System** for continuous learning and performance tracking

## Agent System Architecture

### Core Processing Pipeline

```
Market Question → Research → Analysis → Prediction → Advice → Execution
```

### Agent Flow Diagrams

#### 1. SearchAgent

```mermaid
graph TD
    A([Market Question]) --> C[[Sub-Query Generation]]
    C --> D[Parallel Web Research]
    D --> E{{Follow-up Decision}}
    E -->|Needs More Info| D
    E -->|Sufficient Info| F[/Research Report Synthesis/]
    F --> G(Comprehensive Research Report)

    B1(SubQueryAgent) -.-> C
    B2(FollowUpDecisionAgent) -.-> E
    B3(SynthesisAgent) -.-> F
    B4(Tavily API) ==> D

    %% Lighter colors with good contrast
    style A fill:#bbdefb,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style G fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style D fill:#e1bee7,stroke:#8e24aa,stroke-width:3px,color:#4a148c
    style E fill:#f8bbd9,stroke:#c2185b,stroke-width:3px,color:#ad1457
    style C fill:#ffab91,stroke:#ff5722,stroke-width:2px,color:#bf360c
    style F fill:#a5d6a7,stroke:#4caf50,stroke-width:2px,color:#2e7d32

    %% Agent styling - lighter grays
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#d1c4e9,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a
    style D fill:#e1bee7,stroke:#8e24aa,stroke-width:3px,color:#4a148c
```

- Multi-iteration web research with adaptive follow-up queries
- Parallel query execution with intelligent caching
- Real-time market data aggregation from authoritative sources
- Comprehensive report synthesis with source citations

#### 2. AnalysisAgent

```mermaid
graph TD
    A([Report + Question]) --> C[[Market Analysis Phase]]
    C --> D[/Insight Extraction Phase/]
    D --> E{{Signal Strength Calculation}}
    E --> F(AnalysisResult with Market Insights)

    B1(MarketAnalysisAgent) -.-> C
    B2(InsightExtractionAgent) -.-> D
    B3(Signal Calculator) -.-> E

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style F fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#a5d6a7,stroke:#4caf50,stroke-width:2px,color:#2e7d32
    style D fill:#e1bee7,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a
    style E fill:#f8bbd9,stroke:#c2185b,stroke-width:3px,color:#ad1457

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

- Two-phase analysis: general insights to structured signals
- Market sentiment extraction with confidence weighting
- Signal strength calculation across multiple dimensions
- Risk factor identification and assessment

#### 3. PredictionAgent

```mermaid
graph TD
    A([Analysis + Question + Price]) --> C[[Probability Estimation]]
    C --> D[/Position Sizing Calculation/]
    D --> E{{Kelly Fraction & EV Calculation}}
    E --> F(PredictionResult with Probabilities)

    B1(ProbabilityPredictionAgent) -.-> C
    B2(PositionSizingAgent) -.-> D
    B3(Kelly Calculator) -.-> E

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style F fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e1f5fe,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    style D fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a
    style E fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

- Evidence-based probability calibration
- Kelly Criterion position sizing optimization
- Expected value calculation with risk adjustments
- Confidence interval estimation

#### 4. AdviceAgent

```mermaid
graph TD
    A([Prediction + Context + Scenarios]) --> C[[Analysis Alignment Phase]]
    C --> D[/Conflict Resolution/]
    D --> E{{Risk Assessment}}
    E --> F[Final Decision Generation]
    F --> G(MarketAdviceReport)

    B1(MarketAdviceAgent) -.-> C
    B2(RiskAssessmentAgent) -.-> E
    B3(Decision Framework) -.-> F

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style G fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e1f5fe,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    style D fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style E fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#c62828
    style F fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

- Multi-source analysis alignment and conflict resolution
- Final trading decision with comprehensive risk assessment
- Clear execution recommendations with entry/exit strategies
- Decision confidence scoring

#### 5. ThinkThoroughlyAgent

```mermaid
graph TD
    A([Market Question + Research Report]) --> C{Historical vs Future?}
    C -->|Historical| D[Direct Fact Lookup]
    C -->|Future| E[[Scenario Generation]]
    E --> F[/Scenario Filtering/]
    F --> G{{Research Enrichment}}
    G --> H[Synthesis & Analysis]
    D --> I(EnrichedScenarioAnalysis)
    H --> I

    B1(ResearchDecisionAgent) -.-> C
    B2(ScenarioGenerator) -.-> E
    B3(ScenarioEvaluator) -.-> F
    B4(EnrichmentAgent) -.-> G
    B5(WebResearchAgent) ==> G
    B6(SynthesisAgent) -.-> H

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style I fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#283593
    style D fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#004d40
    style E fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style F fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    style H fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B5 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B6 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

- Intelligent scenario analysis with temporal awareness
- Historical fact verification for past events
- Research enrichment with web-based validation
- Comprehensive scenario reporting and synthesis

### Supporting Systems

#### Market Generation Agents

**MarketEventAgent**: Event verification and status checking

```mermaid
graph TD
    A([Event Description]) --> C[Web Search for Event Status]
    C --> D[/Date & Evidence Extraction/]
    D --> E{{Confidence Assessment}}
    E --> F(EventStatus Result)

    B1(Web Search Tool) -.-> C
    B2(Date Extractor) -.-> D
    B3(Evidence Analyzer) -.-> E

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style F fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e3f2fd,stroke:#0277bd,stroke-width:2px,color:#01579b
    style D fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style E fill:#fff8e1,stroke:#ffa000,stroke-width:2px,color:#e65100

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

**NewsMarketAgent**: Automated market creation from trending news

```mermaid
graph TD
    A([News Category]) --> C[Trending News Search]
    C --> D[[Market Question Generation]]
    D --> E{{Question Validation}}
    E --> F(List of MarketQuestions)

    B1(News Search Tool) -.-> C
    B2(Question Generator) -.-> D
    B3(Question Validator) -.-> E
    B4(Fallback Templates) -.-> E

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style F fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#2e7d32
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style E fill:#fff8e1,stroke:#fb8c00,stroke-width:2px,color:#e65100

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

#### Optimization Systems

**AdvancedKellyOptimizer**: Sophisticated position sizing with multiple Kelly modes

```mermaid
graph TD
    A([Prediction Probability + Market Price]) --> C[[Kelly Fraction Calculation]]
    C --> D[/Risk Adjustments/]
    D --> E{{Portfolio Constraints}}
    E --> F[Stress Testing]
    F --> G(Optimal Position Size)

    B1(Kelly Modes) -.-> C
    B2(Risk Factors) -.-> D
    B3(Correlation Limits) -.-> E
    B4(Monte Carlo) ==> F

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style G fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#2e7d32
    style D fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style E fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style F fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

**MemorySystem**: Performance tracking, pattern detection, and learning insights

```mermaid
graph TD
    A([Prediction Results + Outcomes]) --> C[Prediction Storage]
    C --> D[[Performance Tracking]]
    D --> E{{Pattern Detection}}
    E --> F[/Learning Insights/]
    F --> G(Recommendation Updates)

    B1(SQLite Database) ==> C
    B2(Metrics Calculator) -.-> D
    B3(Pattern Analyzer) -.-> E
    B4(Insight Generator) -.-> F

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style G fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#004d40
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style E fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#e65100
    style F fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

#### Pipeline Orchestration

**PipelineOrchestrator**: System coordination with timeout handling

```mermaid
graph TD
    A([Market Question + Market Price]) --> C[[Research Phase]]
    C --> D[/Scenario Analysis Phase/]
    D --> E{{Prediction Generation}}
    E --> F[Advice Generation]
    F --> G[Memory Storage]
    G --> H(PipelineResult)

    B1(SearchAgent) -.-> C
    B2(ThinkThoroughlyAgent) -.-> D
    B3(AnalysisAgent + PredictionAgent) -.-> E
    B4(AdviceAgent) -.-> F
    B5(MemorySystem) ==> G

    %% Lighter colors with good contrast
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style H fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style C fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#01579b
    style D fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style E fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#e65100
    style F fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#6a1b9a

    %% Agent styling - lighter grays with rounded corners
    style B1 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B2 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B3 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B4 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
    style B5 fill:#cfd8dc,stroke:#607d8b,stroke-width:2px,color:#37474f
```

- **Error Recovery**: Robust error handling with exponential backoff
- **Async Processing**: High-performance concurrent execution

### Pipeline Orchestration Sequence Diagram

```mermaid
sequenceDiagram
    participant Caller as External Caller
    participant Orch as PipelineOrchestrator
    participant Search as SearchAgent
    participant Think as ThinkThoroughlyAgent
    participant Analysis as AnalysisAgent
    participant Predict as PredictionAgent
    participant Advice as AdviceAgent
    participant Memory as MemorySystem

    Note over Caller,Orch: Pipeline Initialization
    Caller->>Orch: analyze_market(question, config, market_price)
    Orch->>Orch: validate_required_keys()
    Orch->>Orch: initialize_agents()
    Orch->>Orch: create_run_id()

    Note over Orch,Search: PHASE 1: RESEARCH
    Orch->>Search: _do_research(question, depth)
    Search->>Search: research(question)
    Search->>Search: generate_subqueries()
    Search->>Search: perform_research() [parallel execution]
    Search->>Search: synthesize_report()
    Search-->>Orch: research_result

    Note over Orch,Think: PHASE 2: SCENARIO ANALYSIS
    alt use_scenario_analysis = true
        Orch->>Think: _do_scenario_analysis(question, research_result)
        Think->>Think: analyze_market_thoroughly()
        alt Historical Question
            Think->>Think: _handle_historical_question()
            Think->>Think: direct_fact_lookup()
        else Future Question
            Think->>Think: _enrich_scenarios_parallel()
            Think->>Think: web_research_enrichment()
        end
        Think-->>Orch: scenario_report
    else
        Orch->>Orch: scenario_report = None
    end

    Note over Orch,Predict: PHASE 3: PREDICTION GENERATION
    Orch->>Analysis: analyze_report(research_result, question)
    Analysis->>Analysis: market_analysis_phase()
    Analysis->>Analysis: insight_extraction_phase()
    Analysis->>Analysis: calculate_signal_strength()
    Analysis-->>Orch: analysis_result

    Orch->>Predict: generate_prediction(analysis_result, question, market_price)
    Predict->>Predict: probability_estimation()
    Predict->>Predict: _calculate_kelly_fraction()
    Predict->>Predict: _calculate_expected_value()
    Predict->>Predict: confidence_assessment()
    Predict-->>Orch: prediction_result

    Note over Orch,Advice: PHASE 4: SYNTHESIS & ADVICE
    Orch->>Advice: _generate_advice(prediction_result, research_result, scenario_report)
    Advice->>Advice: generate_market_advice()
    Advice->>Advice: _generate_primary_advice()
    Advice->>Advice: _generate_risk_assessment()
    Advice->>Advice: conflict_resolution()
    Advice-->>Orch: advice_result

    Note over Orch,Memory: PHASE 5: MEMORY STORAGE
    Orch->>Memory: _store_results(prediction_result, question, config)
    Memory->>Memory: store_prediction()
    Memory->>Memory: update_performance_metrics()
    Memory->>Memory: extract_learning_insights()
    Memory-->>Orch: storage_complete

    Orch->>Orch: build_pipeline_result()
    Orch-->>Caller: PipelineResult{success, recommendation, probability, confidence, reasoning, duration}

    Note over Orch,Memory: Error Handling & Timeouts
    alt Timeout (300s default)
        Orch->>Orch: asyncio.TimeoutError
        Orch->>Orch: _create_error_result()
        Orch-->>Caller: PipelineResult{success=false, errors}
    end

    alt Agent Failure
        Search->>Search: TavilyError/OpenAIError
        Search-->>Orch: Exception
        Orch->>Orch: collect_error()
        Orch->>Orch: _create_error_result()
        Orch-->>Caller: PipelineResult{success=false, errors}
    end
```

### Overall Pipeline Processing Flow

```mermaid
graph TD
    A([Market Question]) --> B[Research Phase]
    B --> C(Research Report)

    C --> D[Scenario Analysis]
    C --> E[Market Analysis]

    D --> F(Scenario Results)
    E --> G(Analysis Results)

    F --> H[Prediction Phase]
    G --> H
    H --> I(Prediction Results)

    I --> J[Advice Phase]
    J --> K(Final Recommendation)

    I --> L[Memory Storage]
    K --> L
    L --> M(Learning Insights)

    %% External inputs
    N(Market Events) -.-> A
    O(News Analysis) -.-> A

    %% Styling with better contrast and readability
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style K fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    style B fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style C fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    style D fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#6a1b9a
    style E fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#2e7d32
    style F fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#ad1457
    style G fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#2e7d32
    style H fill:#fff8e1,stroke:#ffa000,stroke-width:2px,color:#e65100
    style I fill:#fff3e0,stroke:#fb8c00,stroke-width:2px,color:#e65100
    style J fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#c62828
    style L fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#004d40
    style M fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#33691e
    style N fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px,color:#424242
    style O fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px,color:#424242
```

## Project Structure

```
ICP_hack/
│   ├── backend/
│   │   └── canisters/
│   │       ├── market.mo              # Market and AMM logic
│   │       ├── user.mo                # User profiles and leaderboard
│   │       └── insight.mo             # AI insights integration
│   ├── frontend/
│   │   ├── pages/                     # Next.js pages
│   │   ├── components/                # Reusable components
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── utils/                     # Utility functions
│   │   └── types/                     # TypeScript definitions
│   └── agent_pipeline/
│       ├── core/                      # Pipeline orchestration
│       ├── icp_agents/               # Individual AI agents
│       │   ├── search/               # Market research
│       │   ├── analysis/             # Data analysis
│       │   ├── prediction/           # Probability estimation
│       │   ├── advice/               # Trading recommendations
│       │   ├── scenario/             # Scenario analysis
│       │   ├── market_event/         # Event verification
│       │   └── news_market/          # Market generation
│       ├── config/                   # Configuration management
│       ├── cli/                      # Command-line interface
│       ├── utils/                    # Shared utilities
│       └── tests/                    # Test suite
├── dfx.json                          # DFX configuration
└── package.json                      # Root package.json
```

## Features

### Core Functionality

- **Decentralized Markets**: Create and trade prediction markets on ICP
- **Automated Market Making**: LMSR-based price discovery mechanism
- **AI-Powered Insights**: Advanced market analysis and predictions
- **Risk Management**: Kelly Criterion optimization and risk assessment
- **Real-Time Data**: Live market research and trend analysis

### User Experience

- **Modern Interface**: Responsive design with intuitive navigation
- **Wallet Integration**: Multiple wallet options with seamless connection
- **Performance Tracking**: Comprehensive leaderboard and XP system
- **Rich Analytics**: Interactive charts and detailed market insights
- **Mobile Responsive**: Optimized for all device types

### Advanced Analytics

- **Scenario Planning**: Multi-scenario analysis with probability weighting
- **Memory Learning**: Continuous improvement through outcome tracking
- **Signal Processing**: Multi-dimensional market signal extraction
- **Temporal Analysis**: Historical fact verification and trend analysis
- **Confidence Scoring**: Uncertainty quantification for all predictions

## Installation and Setup

### Prerequisites

- Node.js 16 or higher
- DFX SDK for ICP development
- Python 3.9+ for AI agent pipeline
- Git for version control

### Environment Configuration

```bash
# Required API keys
export OPENAI_API_KEY="your_openai_api_key"
export TAVILY_API_KEY="your_tavily_api_key"

# Optional configurations
export ICP_NETWORK="local"  # or "ic" for mainnet
export PIPELINE_TIMEOUT="300"  # 5 minutes default
```

### Installation Steps

1. **Clone Repository**

   ```bash
   git clone <repository-url>
   cd icp_agents/ICP_hack
   ```

2. **Install DFX SDK**

   ```bash
   sh -ci "$(curl -fsSL https://sdk.dfinity.org/install.sh)"
   ```

3. **Install Dependencies**

   ```bash
   # Frontend dependencies
   cd frontend && npm install && cd ..

   # Python dependencies for AI pipeline
   cd agent_pipeline && pip install -r requirements.txt && cd ..
   ```

4. **Start Local Development**

   ```bash
   # Start ICP replica
   dfx start --background

   # Deploy canisters
   dfx deploy

   # Start frontend
   npm run frontend:dev
   ```

## Usage

### Command Line Interface

```bash
# Interactive AI agent pipeline
python -m agent_pipeline.cli.run

# Direct market analysis
python -m agent_pipeline.core.orchestrator
```

### Programmatic API

```python
from agent_pipeline.core.orchestrator import PipelineOrchestrator
from agent_pipeline.config import PipelineConfig

# Configure analysis pipeline
config = PipelineConfig(
    research_depth="standard",
    use_scenario_analysis=True,
    timeout_seconds=180
)

# Initialize orchestrator
orchestrator = PipelineOrchestrator()

# Analyze market
result = await orchestrator.analyze_market(
    "Will Bitcoin reach $100,000 by end of 2025?",
    config,
    market_price=0.35  # Current market probability
)

print(f"Recommendation: {result.recommendation}")
print(f"Probability: {result.probability:.1%}")
print(f"Confidence: {result.confidence}")
```

### Web Interface

1. **Market Creation**

   - Connect wallet (Plug, Stoic, or Internet Identity)
   - Navigate to "Create Market" section
   - Define market parameters and submit with stake
   - AI review and admin validation process

2. **Trading Operations**

   - Browse available markets on homepage
   - View detailed market analysis and AI insights
   - Execute trades using automated market maker
   - Monitor positions and performance metrics

3. **Performance Tracking**
   - Access comprehensive leaderboard system
   - Track XP progression and achievement badges
   - Analyze trading history and success metrics

## Development

### Local Development Commands

```bash
# Start complete development environment
npm run start

# Frontend development only
npm run frontend:dev

# Deploy backend canisters
npm run backend:deploy

# Run AI agent pipeline tests
cd agent_pipeline && python -m pytest tests/

# Type checking
npm run type-check
```

### Production Deployment

```bash
# Deploy to IC mainnet
npm run deploy:ic

# Build optimized frontend
npm run build

# Deploy with custom network
dfx deploy --network ic
```

### Testing

```bash
# Frontend tests
npm run test

# Backend canister tests
dfx canister call market test_all

# AI pipeline tests
cd agent_pipeline && python -m pytest tests/ -v

# Integration tests
npm run test:integration
```

## Configuration

### Agent Pipeline Settings

```python
# config/pipeline_config.py
PIPELINE_CONFIG = {
    "research_depth": "standard",  # quick, standard, deep
    "use_scenario_analysis": True,
    "timeout_seconds": 300,
    "max_follow_ups": 2,
    "cache_duration": 1800,  # 30 minutes
    "kelly_mode": "adaptive"
}
```

### Market Parameters

```motoko
// backend/canisters/market.mo
public type MarketConfig = {
    min_stake: Nat;
    max_markets_per_user: Nat;
    trading_fee_bps: Nat;
    resolution_bond: Nat;
    market_duration_days: Nat;
};
```

## API Reference

### Core Agent Methods

- `SearchAgent.research(question)`: Comprehensive market research
- `AnalysisAgent.analyze_report(report, question)`: Extract trading signals
- `PredictionAgent.generate_prediction(analysis, question)`: Probability estimation
- `AdviceAgent.generate_market_advice(prediction)`: Final recommendations
- `ThinkThoroughlyAgent.analyze_market_thoroughly(question)`: Scenario analysis

### Market Canister Interface

- `create_market(title, description, end_time)`: Create new prediction market
- `place_trade(market_id, outcome, amount)`: Execute trade on market
- `resolve_market(market_id, outcome)`: Resolve market outcome
- `get_market_info(market_id)`: Retrieve market details and pricing

### User Management

- `create_profile(username)`: Initialize user profile
- `update_xp(user_id, points)`: Award experience points
- `get_leaderboard(limit)`: Retrieve top users by performance

## Contributing

### Development Guidelines

1. Fork the repository and create feature branches
2. Follow TypeScript and Python style guidelines
3. Write comprehensive tests for new functionality
4. Update documentation for API changes
5. Submit pull requests with detailed descriptions

### Code Quality Standards

- **TypeScript**: Strict mode with comprehensive type definitions
- **Python**: PEP 8 compliance with type hints
- **Motoko**: Standard formatting with documentation
- **Testing**: Minimum 80% code coverage requirement
- **Documentation**: Inline comments and API documentation

## License

MIT License - See LICENSE file for complete terms and conditions.

## Support

For technical support, bug reports, or feature requests:

- Create GitHub issues for bug reports
- Join community discussions for general questions
- Review documentation for implementation details
- Contact maintainers for critical issues

---

Built with advanced AI agents and decentralized infrastructure for the next generation of prediction markets.
