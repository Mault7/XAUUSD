# XAUUSD Trading Signal Assistant

This repository contains a production-oriented scaffold for a Trading Signal Assistant that analyzes configured assets, builds explainable trade ideas, and sends Telegram alerts without executing trades automatically.

## Status

- Phase 1 complete: architecture definition
- Phase 2 complete: repository scaffold and FastAPI shell
- Phase 3 complete: market data foundation and provider wiring
- Phase 4 complete: indicator engine foundation
- Phase 5 complete: market structure detection
- Phase 6 complete: risk engine foundation
- Phase 7 complete: scoring engine foundation
- Phase 8 complete: alert formatting and publishing foundation
- Phase 9 complete: dashboard/API consolidation
- Phase 10 complete: optimization and production hardening baseline

## Included In Phase 2

- Python 3.12 project setup via `pyproject.toml`
- Clean Architecture package layout under `backend/`
- Typed settings and YAML asset configuration
- Minimal dependency container
- FastAPI application shell with `/health`
- Local Docker Compose stack for API, PostgreSQL, and Redis
- Pytest, Ruff, Black, and MyPy configuration

## Included In Phase 3

- Normalized candle and market snapshot domain models
- `MarketDataProvider` application port
- Market data service with provider-driven asset overview
- Safe provider factory with deterministic in-memory fallback
- Initial MetaTrader5 adapter for real candle ingestion
- `/market/overview` endpoint for provider visibility

## Included In Phase 4

- Explainable indicator snapshot model
- Framework-agnostic indicator engine contract
- Default indicator engine for EMA, RSI, ATR, MACD, ADX, Bollinger Bands, VWAP, and Volume
- Indicator service wired to normalized market snapshots
- `/indicators/overview` endpoint scaffold

## Included In Phase 5

- Structure snapshot model with swing points, levels, and structure events
- Framework-agnostic structure engine contract
- Default structure engine for swing highs/lows, HH/HL/LH/LL, support/resistance, BOS, and CHOCH
- Structure service wired to normalized market snapshots
- `/structure/overview` endpoint scaffold

## Included In Phase 6

- Explainable advisory risk plan model
- Framework-agnostic risk engine contract
- Default risk engine for entry, stop, TP1/TP2/TP3, lot size, and risk/reward
- Risk service wired to market, indicator, and structure analysis
- `/risk/overview` endpoint scaffold

## Included In Phase 7

- YAML-driven scoring weights and defaults
- Explainable score breakdown model with per-factor scoring
- Default scoring engine for weighted confidence and suppression gating
- Scoring service wired to market, indicator, structure, and risk analysis
- `/scoring/overview` endpoint scaffold

## Included In Phase 8

- Alert message model and alerting ports
- Telegram-style alert formatter with explainable message body
- Configurable alert publisher factory with safe log fallback
- Alert preview and dispatch service flow based on score threshold and suppression rules
- `/alerts/preview` and `/alerts/dispatch` endpoint scaffolds

## Included In Phase 9

- Consolidated dashboard read model for market, indicators, structure, risk, scoring, and alerts
- Dashboard service that assembles a single per-asset overview payload
- `/dashboard/overview` endpoint scaffold for frontend/API consumers

## Included In Phase 10

- Shared analysis pipeline service to remove duplicated per-asset computation
- Refactored risk, scoring, alert, and dashboard services onto one analysis context path
- Reduced drift risk between endpoints and better foundation for persistence, caching, and scheduling

## Telegram Bot

- Polling runner available at `backend/telegram_bot/runner.py`
- Commands menu is registered automatically with Telegram via `set_my_commands`
- Initial commands: `/start`, `/help`, `/health`, `/analyze`, `/scan`
- Reply keyboard buttons are generated automatically from enabled assets
- Run it with `python -m backend.telegram_bot.runner`

## Fixed-Loss Risk Mode

- Set `RISK_MODE=fixed_loss` to use a global money-risk model instead of account-percent sizing
- `MAX_LOSS_USD` controls the maximum advisory loss per signal
- `FIXED_LOT_SIZE` keeps a fixed MT5 volume such as `0.01`
- In this mode the stop loss is derived from the symbol specification returned by MT5 and targets are anchored to nearby market structure when available

## Quick Start

1. Create a virtual environment and install dependencies with `pip install -e .[dev]`.
2. Copy `.env.example` to `.env`.
3. Run the API with `uvicorn backend.main:app --reload`.
4. Visit `http://localhost:8000/health`.

## References

- [Phase 1 architecture](docs/phase-1-architecture.md)
