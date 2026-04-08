\---

trigger: always\_on

\---



\# APEX Project Rules — Always Active



\## Project Identity

APEX (Autonomous Predictive Exchange) is a self-evolving, trustless, multi-agent AI trading organism built for the lablab.ai AI Trading Agents Hackathon (deadline April 12, 2026).



\## Non-Negotiable Build Standards

\- Every file must be COMPLETE. No stubs, no TODOs, no placeholders, no "implement later" comments.

\- Every function must have a docstring explaining what it does, what it takes, what it returns.

\- Every async call must have try/catch with user-visible graceful error handling.

\- Every module must have a working \_\_main\_\_ block or entry point for standalone testing.

\- No hardcoded secrets — all keys come from .env via python-dotenv or process.env.



\## Stack

\- Python 3.11+, CrewAI, LangGraph, web3.py, python-dotenv

\- Node.js 20+, Express, WebSocket (ws library)

\- React 18, Recharts, Tailwind CSS

\- Azure Cosmos DB, Azure Container Apps, Azure Static Web Apps

\- Kraken CLI (Rust binary with built-in MCP server)

\- Base L2 testnet for ERC-8004 on-chain contracts



\## File Ownership (who owns what)

\- apex-core.py → DR. ZARA OKAFOR (Strategy Orchestrator)

\- apex-architecture.py → PROF. KWAME ASANTE (System Design)

\- apex-learn.py → DR. AMARA DIALLO (ML \& Self-Rewriting)

\- apex-data.py → DR. YUKI TANAKA (Market Intelligence)

\- apex-sentiment.py + apex-nlp.py → DR. JABARI MENSAH (NLP)

\- apex-executor.py → ENGR. MARCUS ODUYA (Kraken Execution)

\- apex-identity.py → DR. PRIYA NAIR (ERC-8004 \& On-Chain)

\- apex-risk.py → DR. SIPHO NKOSI (Risk Management)

\- apex-rl.py → DR. LIN QIANRU (Reinforcement Learning)

\- apex/dashboard/ → ENGR. FATIMA AL-RASHID (React UI)

\- apex/contracts/ → DR. PRIYA NAIR (Solidity)

\- apex/api/server.js → PROF. KWAME ASANTE (Node.js API)



\## Design System (dashboard only)

\- --apex-deep: #0A1628 (background)

\- --apex-surface: #0D2040 (cards/panels)

\- --apex-primary: #1a56db (primary actions)

\- --apex-bright: #3b82f6 (hover/active)

\- --apex-gold: #F5A623 (reputation, PnL positive)

\- --apex-success: #10b981 (trade success)

\- --apex-danger: #ef4444 (circuit breaker, failure)

\- Headings: Inter 700

\- UI: DM Sans 400/500

\- Data/numbers: JetBrains Mono

