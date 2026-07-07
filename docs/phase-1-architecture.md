# Trading Signal Assistant MVP Architecture

## Objective

Design a production-grade Trading Signal Assistant that analyzes multiple assets, generates explainable trading signals, and sends alerts to Telegram without placing trades automatically.

## Architectural Principles

- Clean Architecture with strict inward dependency flow.
- Domain-centric design for trading concepts and signal logic.
- Configuration-first extensibility for assets, timeframes, thresholds, and strategies.
- Explainability as a first-class requirement in every analysis stage.
- Plugin-based strategies and market providers.
- Deterministic, testable services with explicit interfaces.

## High-Level Layers

### Domain

Contains pure business models and rules with no framework dependencies.

Core responsibilities:

- Trading entities and value objects
- Signal semantics
- Market structure concepts
- Indicator result contracts
- Scoring contracts
- Risk model contracts
- Strategy interfaces

### Application

Coordinates use cases and orchestration across domain services.

Core responsibilities:

- Market analysis workflows
- Signal generation pipeline
- News filter orchestration
- Scheduling use cases
- Alert dispatch use cases
- Persistence coordination

### Infrastructure

Implements external integrations and technical adapters.

Core responsibilities:

- MetaTrader5 adapters
- TradingView webhook ingestion
- Economic calendar providers
- PostgreSQL repositories
- Redis caching
- Telegram delivery
- YAML configuration loading
- Scheduler wiring

### API

Exposes HTTP endpoints and webhook entry points.

Core responsibilities:

- Health checks
- Dashboard/API endpoints
- TradingView webhook endpoints
- Signal query endpoints
- Administrative configuration views

## Proposed Directory Layout

```text
backend/
  domain/
    entities/
    value_objects/
    services/
    repositories/
    strategies/
  application/
    use_cases/
    dto/
    services/
    ports/
  infrastructure/
    config/
    db/
    cache/
    market/
    news/
    alerts/
    scheduler/
    strategies/
  api/
    http/
    webhooks/
    schemas/
    dependencies/
  tests/
    unit/
    integration/
docs/
docker/
frontend/
```

## Core Domain Model

### Entities

- `Asset`
- `MarketSnapshot`
- `IndicatorSnapshot`
- `StructureSnapshot`
- `SmartMoneySnapshot`
- `TrendAssessment`
- `RiskPlan`
- `Signal`
- `SignalOutcome`

### Value Objects

- `PriceLevel`
- `Timeframe`
- `SignalDirection`
- `ConfidenceScore`
- `StrategyName`
- `NewsImpact`
- `RiskRewardProfile`

## Key Application Use Cases

- `AnalyzeMarketUseCase`
- `GenerateSignalUseCase`
- `ScoreSignalUseCase`
- `FilterByNewsUseCase`
- `CreateRiskPlanUseCase`
- `SendTelegramAlertUseCase`
- `PersistSignalUseCase`
- `RunScheduledAnalysisUseCase`

## Primary Ports and Interfaces

### Market Data Ports

- `MarketDataProvider`
- `EconomicCalendarProvider`
- `WebhookEventIngestor`

### Persistence Ports

- `SignalRepository`
- `IndicatorRepository`
- `MarketSnapshotRepository`
- `ConfigurationRepository`

### Delivery Ports

- `AlertPublisher`
- `DashboardQueryService`

### Strategy Contracts

Each strategy plugin must implement:

- `analyze(context) -> StrategyAnalysis`
- `score(context) -> ScoreBreakdown`
- `reason(context) -> list[str]`
- `generate_signal(context) -> Signal | None`

## Analysis Pipeline

```text
Scheduler / Webhook Trigger
  -> Load asset configuration
  -> Fetch and normalize market data
  -> Build multi-timeframe market context
  -> Compute indicators
  -> Detect market structure
  -> Detect smart money signals
  -> Evaluate trend engine
  -> Apply strategy plugins
  -> Build risk plan
  -> Score opportunity
  -> Apply news suppression / confidence reduction
  -> Persist analysis and signal
  -> Publish Telegram alert if threshold met
```

## Extensibility Model

### Assets

Assets are added through YAML configuration only.

Configurable dimensions:

- Symbol mapping by provider
- Enabled strategies
- Timeframes
- Trading session rules
- Risk profile
- Alert thresholds
- News sensitivity

### Strategies

Strategies are registered as plugins through a strategy factory.

Requirements:

- No direct dependency on FastAPI, SQLAlchemy, Telegram, or MT5
- Read from a common analysis context
- Return structured reasons and partial scores
- Be independently unit testable

### Providers

Provider adapters implement ports for:

- MT5 price/history data
- TradingView webhook events
- Economic calendar feeds

## Multi-Timeframe Trend Engine Design

Trend engine consumes candles from:

- `MN`
- `W1`
- `D1`
- `H4`
- `H1`
- `M15`
- `M5`

Output:

- Direction: bullish, bearish, sideways
- Alignment score
- Supporting reasons
- Conflict explanation when timeframes disagree

## Explainability Contract

Every major component returns:

- `value`
- `direction`
- `strength`
- `explanation`

This applies to indicators and should be mirrored by structure, trend, smart-money, risk, and scoring outputs where applicable.

## Scoring Engine Design

Scoring uses weighted components defined in YAML, not hardcoded.

Initial categories:

- Trend alignment
- Market structure
- Support/resistance quality
- RSI
- ATR
- MACD
- ADX
- Volume
- Smart money confluence
- News filter

Outputs:

- Total score
- Per-factor breakdown
- Confidence percentage
- Suppression flag
- Human-readable reasoning

## Risk Engine Design

Risk engine is advisory only.

Outputs:

- Suggested entry
- Stop loss
- TP1
- TP2
- TP3
- Risk percentage
- Lot size
- Risk/reward profile

The engine must annotate how levels were derived.

## Data Storage Design

### PostgreSQL

Primary system of record for:

- Signals
- Indicator snapshots
- Score breakdowns
- Risk plans
- Reasons/explanations
- Historical outcomes

### Redis

Used for:

- Recent market snapshot cache
- Computation reuse
- Scheduler coordination
- Rate-limited alert deduplication

## Deployment Topology

### Backend Services

- FastAPI service
- Worker/scheduler service
- PostgreSQL
- Redis

### External Dependencies

- MetaTrader5 terminal/API
- Telegram Bot API
- Economic calendar provider

## Non-Functional Requirements

- Full type coverage for critical services
- Structured logging
- Deterministic configuration loading
- Testable strategy isolation
- Dockerized local environment
- CI for lint, type-check, and tests

## Phase Boundaries

### Phase 1

- Architecture definition
- Core domain boundaries
- Port/interface design
- Data flow design

### Phase 2

- Repository scaffold
- Python project setup
- FastAPI app shell
- Dependency injection wiring
- Test framework and tooling

## Initial Decisions

1. Use a modular monolith for the MVP to reduce operational complexity while preserving clear boundaries.
2. Keep domain logic framework-agnostic.
3. Model strategies and providers as plugins behind interfaces/factories.
4. Centralize configuration in YAML with validated loading into typed settings objects.
5. Persist every signal decision and explanation for auditability.

## Open Design Questions For Phase 2+

1. Which economic calendar provider will be used first for MVP integration?
2. Should TradingView ingestion be limited to webhook-triggered enrichment or used as a primary signal trigger?
3. What level of dashboard scope is needed for MVP: read-only analytics or operator controls too?
