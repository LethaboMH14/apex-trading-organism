# APEX — Complete Provider Strategy & LLM Router
**All 9 Cloud APIs + Ollama Local — Fully Wired**

---

## PART 1 — Your Complete .env (fill in real keys)

Replace `APEX/.env` with this complete version:

```env
# ============================================================
# APEX ENVIRONMENT — COMPLETE CONFIGURATION
# ============================================================

# --- APEX SYSTEM ---
APEX_PAPER_MODE=true                          # NEVER change to false until Phase 6
APEX_SYMBOLS=XBTUSD,ETHUSD,SOLUSD
APEX_CYCLE_INTERVAL=60                        # seconds between trading cycles
APEX_LOG_LEVEL=INFO

# --- KRAKEN ---
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_API_SECRET=your_kraken_secret_here
KRAKEN_CLI_PATH=kraken                        # assumes it's on PATH

# --- PRISM / STRYKR ---
PRISM_API_KEY=LABLAB                          # your promo code
PRISM_API_URL=https://api.prism.strykr.ai

# --- ON-CHAIN (ERC-8004, Base Goerli) ---
BASE_RPC_URL=https://goerli.base.org
APEX_PRIVATE_KEY=your_wallet_private_key_here
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
PINATA_API_KEY=your_pinata_key_here

# --- AZURE (Infrastructure + AI fallback) ---
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_GPT4O=gpt-4o
AZURE_OPENAI_DEPLOYMENT_GPT4_TURBO=gpt-4-turbo
AZURE_COSMOS_CONNECTION_STRING=your_cosmos_connection_string_here

# ============================================================
# LLM PROVIDERS — PRIMARY MODELS (used by apex-llm-router.py)
# ============================================================

# --- OPENROUTER (DeepSeek R1 + Qwen + fallbacks) ---
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# --- GROQ (ultra-fast inference — LLaMA 3.3 70B) ---
GROQ_API_KEY=your_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1

# --- GOOGLE AI (Gemini 2.5 Pro — long context) ---
GOOGLE_API_KEY=your_key_here

# --- BYTEPLUS (NLP sentiment — 5M free daily tokens) ---
BYTEPLUS_API_KEY=your_key_here
BYTEPLUS_BASE_URL=https://ark.byteplusapi.com/v1

# --- SAMBANOVA (Qwen2.5 72B — fast large model) ---
SAMBANOVA_API_KEY=your_key_here
SAMBANOVA_BASE_URL=https://api.sambanova.ai/v1

# --- NVIDIA (Nemotron — creative/UI tasks) ---
NVIDIA_API_KEY=your_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# --- MISTRAL (Codestral — code quality + testing) ---
MISTRAL_API_KEY=your_key_here
MISTRAL_BASE_URL=https://api.mistral.ai/v1

# --- DEEPSEEK (direct API — math reasoning backup) ---
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# --- OLLAMA (local — offline fallback, no API key needed) ---
OLLAMA_HOST=http://localhost:11434

# --- ALIBABA (disabled — enable billing first) ---
# ALIBABA_API_KEY=your_key_here
# ALIBABA_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# ============================================================
# ROO CODE PROVIDER DEFAULTS (set these in Roo Code UI too)
# Primary: OpenRouter | Fast: Groq | Local: Ollama
# ============================================================
ROO_DEFAULT_PROVIDER=openrouter
ROO_DEFAULT_MODEL=qwen/qwen3-72b-instruct
ROO_FAST_PROVIDER=groq
ROO_FAST_MODEL=llama-3.3-70b-versatile
ROO_LOCAL_MODEL=deepseek-coder:latest
```

---

## PART 2 — Agent → Model Assignment (The Master Map)

| Agent | Role | Primary Model | Provider | Why | Fallback |
|-------|------|--------------|----------|-----|----------|
| DR. ZARA | Strategy Orchestrator | `deepseek/deepseek-r1` | OpenRouter | Best reasoning, routes complex decisions | GPT-4o (Azure) |
| PROF. KWAME | Architecture | `gpt-4o` | Azure | System design, infra decisions, reliable | Qwen3-72B (OpenRouter) |
| DR. AMARA | ML & Strategy Rewriter | `deepseek/deepseek-r1` | OpenRouter | Mathematical reasoning, Sharpe optimization | DeepSeek API direct |
| DR. YUKI | Market Intelligence | `gemini-2.5-pro` | Google AI | 2M context window, reads full codebase + docs | Gemini 2.5 Flash |
| DR. JABARI | NLP & Sentiment | `byteplus/sentiment` | BytePlus | 5M free daily tokens, built for NLP at scale | LLaMA-3.3-70B (Groq) |
| ENGR. MARCUS | Execution | `llama-3.3-70b-versatile` | Groq | Ultra-fast (under 1s), execution needs speed | Qwen2.5-72B (SambaNova) |
| DR. PRIYA | ERC-8004 / On-Chain | `gpt-4-turbo` | Azure | Best Solidity + cryptographic reasoning | GPT-4o (Azure) |
| DR. SIPHO | Risk Management | `qwen2.5-72b-instruct` | SambaNova | Reliable, fast, good at rules-based logic | LLaMA-3.3-70B (Groq) |
| DR. LIN | Reinforcement Learning | `qwen/qwen3-72b-instruct` | OpenRouter | Strong math + RL theory | DeepSeek R1 |
| ENGR. FATIMA | Dashboard / React | `gemini-2.5-flash` | Google AI | Fast, great at UI/component generation | Codestral (Mistral) |
| DR. SARA | Testing & Verification | `codestral-latest` | Mistral | Purpose-built for code testing and review | Qwen2.5-Coder (SambaNova) |
| ENGR. CHIOMA | Design & Presentation | `meta/llama-3.1-405b` | NVIDIA | Creative tasks, presentation content | Gemini 2.5 Flash |

**Local Ollama models (when offline or rate-limited):**
- `deepseek-coder:latest` → fallback for DR. AMARA, DR. SARA
- `qwen2.5-coder:latest` → fallback for ENGR. FATIMA, ENGR. MARCUS
- `llama3.1:latest` → fallback for DR. ZARA, DR. SIPHO
- `phi4:latest` → fallback for PROF. KWAME (lightweight architecture help)

---

## PART 3 — Windsurf Prompt: Build apex-llm-router.py

Paste this into Cascade to build the actual Python LLM router all agents will use:

```
You are PROF. KWAME ASANTE, Chief Architecture Officer of APEX.

Your standard: "Every component must survive a 3am failure with zero human intervention."

Build the file `apex/apex-llm-router.py` — the unified LLM routing layer that every APEX agent 
calls to get a model response. This is the nervous system that connects all 12 agents to their 
assigned AI providers.

REQUIREMENTS:

--- LLMProvider enum ---
Define an enum with all providers:
OPENROUTER, GROQ, GOOGLE, BYTEPLUS, SAMBANOVA, NVIDIA, MISTRAL, DEEPSEEK, AZURE_OPENAI, OLLAMA

--- ModelConfig dataclass ---
Fields: provider (LLMProvider), model_id (str), max_tokens (int), temperature (float), 
        timeout_seconds (int), cost_tier ("free"|"cheap"|"moderate"|"expensive")

--- AGENT_MODEL_MAP dict ---
Maps each of the 12 agent names to a ModelConfig (primary) and a fallback ModelConfig.
Use these exact assignments:

DR_ZARA:      primary=deepseek/deepseek-r1 via OPENROUTER,        fallback=gpt-4o via AZURE_OPENAI
PROF_KWAME:   primary=gpt-4o via AZURE_OPENAI,                    fallback=qwen/qwen3-72b via OPENROUTER  
DR_AMARA:     primary=deepseek/deepseek-r1 via OPENROUTER,        fallback=deepseek-chat via DEEPSEEK
DR_YUKI:      primary=gemini-2.5-pro via GOOGLE,                  fallback=gemini-2.5-flash via GOOGLE
DR_JABARI:    primary=byteplus/sentiment via BYTEPLUS,             fallback=llama-3.3-70b-versatile via GROQ
ENGR_MARCUS:  primary=llama-3.3-70b-versatile via GROQ,           fallback=qwen2.5-72b-instruct via SAMBANOVA
DR_PRIYA:     primary=gpt-4-turbo via AZURE_OPENAI,               fallback=gpt-4o via AZURE_OPENAI
DR_SIPHO:     primary=qwen2.5-72b-instruct via SAMBANOVA,         fallback=llama-3.3-70b-versatile via GROQ
DR_LIN:       primary=qwen/qwen3-72b-instruct via OPENROUTER,     fallback=deepseek/deepseek-r1 via OPENROUTER
ENGR_FATIMA:  primary=gemini-2.5-flash via GOOGLE,                fallback=codestral-latest via MISTRAL
DR_SARA:      primary=codestral-latest via MISTRAL,               fallback=qwen2.5-coder via SAMBANOVA
ENGR_CHIOMA:  primary=nvidia/llama-3.1-nemotron-70b via NVIDIA,   fallback=gemini-2.5-flash via GOOGLE

--- OllamaFallback dict ---
Maps each agent to their Ollama model (last-resort offline fallback):
DR_ZARA→llama3.1:latest, PROF_KWAME→phi4:latest, DR_AMARA→deepseek-coder:latest,
DR_YUKI→llama3.1:latest, DR_JABARI→llama3.1:latest, ENGR_MARCUS→qwen2.5-coder:latest,
DR_PRIYA→llama3.1:latest, DR_SIPHO→llama3.1:latest, DR_LIN→deepseek-coder:latest,
ENGR_FATIMA→qwen2.5-coder:latest, DR_SARA→deepseek-coder:latest, ENGR_CHIOMA→llama3.1:latest

--- LLMRouter class ---

__init__:
  - Loads all API keys from environment (python-dotenv)
  - Initializes OpenAI-compatible clients for all providers:
    * OpenRouter: openai.AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
    * Groq: openai.AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)
    * SambaNova: openai.AsyncOpenAI(base_url=SAMBANOVA_BASE_URL, api_key=SAMBANOVA_API_KEY)
    * NVIDIA: openai.AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
    * Mistral: openai.AsyncOpenAI(base_url=MISTRAL_BASE_URL, api_key=MISTRAL_API_KEY)
    * DeepSeek: openai.AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)
    * Azure: openai.AsyncAzureOpenAI(endpoint, api_key, api_version="2024-02-01")
    * Google: google.generativeai configured with GOOGLE_API_KEY
    * BytePlus: openai.AsyncOpenAI(base_url=BYTEPLUS_BASE_URL, api_key=BYTEPLUS_API_KEY)
    * Ollama: openai.AsyncOpenAI(base_url=OLLAMA_HOST+"/v1", api_key="ollama")
  - Tracks call counts and error counts per provider in self.stats dict

async call(agent_name: str, messages: list, system_prompt: str = None) -> dict:
  - Looks up agent's primary ModelConfig from AGENT_MODEL_MAP
  - Attempts primary model
  - On any exception (rate limit, timeout, API error): logs warning, tries fallback model
  - On fallback failure: tries Ollama local model
  - On Ollama failure: raises LLMRouterError with full context
  - Returns: {response: str, agent: str, model_used: str, provider_used: str, 
              latency_ms: int, fallback_used: bool, tokens_used: int}
  - Logs every call: agent, model, latency, success/failure

async health_check() -> dict:
  - Sends a minimal test prompt ("ping") to each provider
  - Returns {provider: "ok"|"slow"|"error"} for all 10 providers
  - Marks slow if latency > 3000ms
  - Does NOT raise — always returns a result even if all providers fail

get_stats() -> dict:
  - Returns call counts, error counts, avg latency per provider
  - Includes: total_calls, total_errors, total_cost_estimate (rough $)
  - Cost estimates: Groq=free, Ollama=free, BytePlus=free(under limit), 
                    OpenRouter/DeepSeek=cheap, SambaNova/NVIDIA/Mistral=cheap, 
                    Google/Azure=moderate

--- Convenience wrapper functions (module-level) ---
Build these so any agent file can call them without instantiating the router:

async def ask_zara(messages, system=None) -> str
async def ask_kwame(messages, system=None) -> str
async def ask_amara(messages, system=None) -> str
async def ask_yuki(messages, system=None) -> str
async def ask_jabari(messages, system=None) -> str
async def ask_marcus(messages, system=None) -> str
async def ask_priya(messages, system=None) -> str
async def ask_sipho(messages, system=None) -> str
async def ask_lin(messages, system=None) -> str
async def ask_fatima(messages, system=None) -> str
async def ask_sara(messages, system=None) -> str
async def ask_chioma(messages, system=None) -> str

Each returns just the response string (not the full dict).

--- if __name__ == "__main__" ---
Run health_check() on all providers and print a formatted status table:

  Provider      | Status  | Latency
  --------------|---------|--------
  OpenRouter    | ✅ ok   | 412ms
  Groq          | ✅ ok   | 98ms
  Google        | ✅ ok   | 891ms
  BytePlus      | ✅ ok   | 234ms
  SambaNova     | ✅ ok   | 301ms
  NVIDIA        | ✅ ok   | 445ms
  Mistral       | ✅ ok   | 267ms
  DeepSeek      | ✅ ok   | 523ms
  Azure OpenAI  | ✅ ok   | 712ms
  Ollama        | ✅ ok   | 45ms

Then run one test call per agent (ask a one-line question) and print results.

--- Dependencies ---
pip install openai google-generativeai python-dotenv

Full docstrings, complete error handling, no TODOs, no stubs.
```

---

## PART 4 — How Other Agent Files Use the Router

Once `apex-llm-router.py` is built, every other file imports from it like this:

```python
# In apex-learn.py (DR. AMARA):
from apex_llm_router import ask_amara, ask_lin

# Use in any async function:
response = await ask_amara([
    {"role": "user", "content": f"Analyze these trades and suggest new signal weights: {trades_json}"}
])

# In apex-risk.py (DR. SIPHO):
from apex_llm_router import ask_sipho

risk_assessment = await ask_sipho([
    {"role": "user", "content": f"Should I approve this trade? Signal: {signal}, Exposure: {exposure}"}
])
```

Add this import line to the Cascade prompt for **every** subsequent file you build:

```
IMPORTANT: Import LLM calls from apex_llm_router.py using the convenience function 
for this agent (e.g., `from apex_llm_router import ask_amara`). 
Do NOT hardcode any API client directly in this file.
```

---

## PART 5 — Roo Code Setup (Multi-Provider UI)

Open Roo Code in Windsurf (`Ctrl+Shift+P` → "Roo Code: Open"), then set up these profiles:

### Profile 1 — "APEX Fast" (daily coding)
- Provider: **Groq**
- Model: `llama-3.3-70b-versatile`
- Use for: quick fixes, refactors, short file edits
- Why: free tier, sub-100ms responses

### Profile 2 — "APEX Deep" (architecture/complex logic)
- Provider: **OpenRouter**
- Model: `deepseek/deepseek-r1`
- Use for: algorithm design, CrewAI wiring, complex debugging
- Why: best reasoning model, cheap per token

### Profile 3 — "APEX Long" (full codebase review)
- Provider: **Google AI**
- Model: `gemini-2.5-pro`
- Use for: reviewing multiple files at once, architecture Q&A
- Why: 2M token context window — can hold your entire project

### Profile 4 — "APEX Offline" (no internet)
- Provider: **Ollama**
- Model: `deepseek-coder:latest`
- Use for: coding when offline or all cloud APIs are rate-limited
- Why: runs on your machine, free, private

---

## PART 6 — Ollama Model Recommendations for 8GB RAM

Based on your machine constraint, these are the right models to have installed:

```bash
# Pull these — all run well under 8GB VRAM/RAM
ollama pull deepseek-coder:6.7b          # Best code model at this size
ollama pull qwen2.5-coder:7b             # Excellent for React/JS/Python  
ollama pull llama3.1:8b                  # General reasoning fallback
ollama pull phi4:latest                  # Microsoft's efficient model (~4GB)

# Test all are working:
ollama list
ollama run deepseek-coder:6.7b "Write a Python hello world"
```

**Note:** The `deepseek-coder:latest` in your existing config points to the full 33B model — too large for 8GB. Use `deepseek-coder:6.7b` instead. Your `.env` already has `OLLAMA_HOST=http://localhost:11434` which is correct.

---

## PART 7 — Updated Windsurf Rules File

Add this section to your existing `APEX/.windsurf/rules/apex-project.md`:

```markdown
## LLM Router (CRITICAL — read before building any agent file)

The file `apex/apex-llm-router.py` is the ONLY place API clients are initialized.
Every other file imports from it. NEVER initialize an OpenAI/Groq/Google client 
directly in any agent file.

Import pattern:
  from apex_llm_router import ask_[agentname]

Agent → correct import:
  apex-core.py        → ask_zara
  apex-architecture.py → ask_kwame
  apex-learn.py       → ask_amara
  apex-data.py        → ask_yuki
  apex-sentiment.py   → ask_jabari
  apex-executor.py    → ask_marcus
  apex-identity.py    → ask_priya
  apex-risk.py        → ask_sipho
  apex-rl.py          → ask_lin
  apex-nlp.py         → ask_jabari
  api/server.js       → calls Python API (no direct LLM calls in Node)
  dashboard/          → no LLM calls in frontend

Provider priority order (router handles this automatically):
  1. Primary cloud model (from AGENT_MODEL_MAP)
  2. Fallback cloud model
  3. Ollama local model
  4. Raise LLMRouterError

Run `python apex-llm-router.py` to health-check all providers before starting a build session.
```

---

## PART 8 — Build Order with Router Integration

Updated build order now that the router exists:

```
Phase 1 (TODAY):
  1. apex-llm-router.py   ← BUILD THIS FIRST (§3 prompt above)
  2. Run health check     ← python apex-llm-router.py
  3. apex-core.py         ← uses ask_zara (from APEX_PROMPTS.md §1)
  4. apex-architecture.py ← uses ask_kwame

Phase 2:
  5. apex-data.py         ← uses ask_yuki
  6. apex-sentiment.py    ← uses ask_jabari
  7. apex-learn.py        ← uses ask_amara + ask_lin
  8. apex-rl.py           ← uses ask_lin

Phase 3:
  9. apex-executor.py     ← uses ask_marcus
  10. apex-risk.py        ← uses ask_sipho
  11. apex-identity.py    ← uses ask_priya

Phase 4:
  12. apex-nlp.py         ← uses ask_jabari

Phase 5:
  13. api/server.js       ← no LLM calls
  14. dashboard/          ← no LLM calls
  15. contracts/          ← uses ask_priya for audit
```

---

*APEX — Every provider has a purpose. Every agent has a voice.*
