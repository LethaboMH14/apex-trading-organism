# APEX — Phase 3 Setup Reminder
# paste this into Cascade OR read it yourself when you reach Phase 3 (Days 5-7)

---

## BEFORE YOU START PHASE 3 — Complete This First

Phase 3 builds: apex-executor.py, apex-risk.py, apex-identity.py
These files need real credentials. Do all of this BEFORE pasting the Phase 3 prompts.

---

### ✅ STEP 1 — Create a throwaway MetaMask wallet (10 mins)

This wallet is ONLY for APEX on-chain testing. Never put real money in it.

1. Open MetaMask → Create a new account (not your main one)
2. Name it "APEX Testnet"
3. Switch network to Base Goerli testnet
   - If not listed: Add network manually
   - Network name: Base Goerli
   - RPC URL: https://goerli.base.org
   - Chain ID: 84531
   - Symbol: ETH
4. Export private key:
   MetaMask → click account → three dots → Account Details → Export Private Key
5. Paste into .env:
   APEX_PRIVATE_KEY=0x...your key here...
6. Copy the wallet ADDRESS (not the key) — you'll need it for contract deployment

---

### ✅ STEP 2 — Get testnet ETH for gas fees (5 mins)

You need a tiny amount of Base Goerli ETH to deploy contracts and sign transactions.
It's free — use a faucet:

- Go to: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
- OR: https://faucet.quicknode.com/base/goerli
- Paste your APEX wallet address
- Request ETH — you'll get 0.01-0.1 ETH, enough for everything

---

### ✅ STEP 3 — Create Pinata account for IPFS (5 mins)

DR. PRIYA uses Pinata to store Agent Card JSON on IPFS.

1. Go to: https://pinata.cloud
2. Sign up free (no credit card needed)
3. Go to: API Keys → New Key
4. Permissions: pinFileToIPFS, pinJSONToIPFS
5. Copy the API key and paste into .env:
   PINATA_API_KEY=your key here
   PINATA_API_SECRET=your secret here  ← add this line to .env too

---

### ✅ STEP 4 — Deploy the Solidity contracts (Phase 3, Day 6)

After you build apex/contracts/ using the §17-19 prompt from APEX_WINDSURF_PROMPTS.md:

1. Install Hardhat in the APEX project:
   npm init -y
   npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

2. In Windsurf terminal:
   npx hardhat run scripts/deploy.js --network base-goerli

3. Copy the deployed contract addresses from the output and paste into .env:
   IDENTITY_REGISTRY_ADDRESS=0x...
   REPUTATION_REGISTRY_ADDRESS=0x...
   VALIDATION_REGISTRY_ADDRESS=0x...

---

### ✅ STEP 5 — Create a second READ-ONLY Kraken key for judges (Phase 6)

Do this ONLY when submitting to lablab.ai — not before.

1. Kraken → Security → API → Create new key
2. Name it: "APEX Lablab Submission"
3. Select ONLY:
   - ✅ Query (Funds)
   - ✅ Query open orders & trades
   - ✅ Query closed orders & trades
   - ✅ Query ledger entries
   - ❌ Everything else — especially NO Withdraw
4. Submit this key (not your trading key) to lablab.ai

---

## CASCADE PROMPT — Paste this when starting Phase 3

```
I am now starting Phase 3 of APEX (Days 5-7).

Before we build, confirm:
- apex-executor.py needs KRAKEN_API_KEY, KRAKEN_API_SECRET, APEX_PAPER_MODE=true
- apex-identity.py needs APEX_PRIVATE_KEY, BASE_RPC_URL, PINATA_API_KEY
- apex-risk.py has no external dependencies beyond the existing router

All three .env values are now set. APEX_PAPER_MODE is true — no live trading yet.
Contract addresses (IDENTITY_REGISTRY_ADDRESS etc) will be filled after deployment in Step 4.

Now build apex-executor.py using the ENGR. MARCUS prompt from APEX_WINDSURF_PROMPTS.md §7.
Read .windsurf/rules/apex-project.md first.
```

---

## YOUR .ENV CHECKLIST FOR PHASE 3

Run this mentally before starting — all should be filled:

- [ ] KRAKEN_API_KEY — ✅ done
- [ ] KRAKEN_API_SECRET — ✅ done  
- [ ] APEX_PAPER_MODE=true — ✅ confirm this is true
- [ ] APEX_PRIVATE_KEY — ⏳ do Step 1 above
- [ ] BASE_RPC_URL=https://goerli.base.org — ✅ already correct
- [ ] PINATA_API_KEY — ⏳ do Step 3 above
- [ ] IDENTITY_REGISTRY_ADDRESS — ⏳ filled after contract deploy (Step 4)
- [ ] REPUTATION_REGISTRY_ADDRESS — ⏳ filled after contract deploy (Step 4)
- [ ] VALIDATION_REGISTRY_ADDRESS — ⏳ filled after contract deploy (Step 4)

---

*Save this file. Read it the morning you start Phase 3.*
*APEX — Built by a company of minds. Governed by a standard of perfection.*
