# 🏪 Royal Scepter Shop Assistant

An AI-powered customer assistant for **Royal Scepter Computers & Video Games** — a computer and phone retail shop in Lagos, Nigeria. It answers customer questions about products, prices, Nigerian VAT, delivery fees and warranty using an LLM agent with tools — never hallucinated facts.

## 🔗 Live Demo
Deployed on Streamlit Community Cloud: **https://royal-scepter-assistant-dbfzn6vcn3x2wbb7az987t.streamlit.app/**

*(Hugging Face Space also available: https://huggingface.co/spaces/sixtus70/royal-scepter-assistant)*

## ✨ What it does
Customers can ask in plain language:
- 💰 "How much is the iPhone 13 with VAT?" — exact price + 7.5% Nigerian VAT
- 🖥️ "Which is your cheapest laptop?" — real catalog lookups
- 🚚 "Delivery to Lagos mainland for ₦265,000?" — delivery fees, free over ₦500,000 within Lagos
- 🛡️ "What's the warranty on the MacBook Air?" — warranty terms from shop policies
- ❓ And when a product doesn't exist, it says so honestly instead of inventing an answer

## 🛡️ Security (red-teamed)
Built with a hardened system prompt + output validation. Tested against 5 attack classes:
prompt injection, fake authority ("I'm the owner"), hallucination bait, defamation bait, and code-execution attempts. All refused safely.

## 🏗️ Architecture
| Layer | Tech |
|---|---|
| LLM | Groq API (openai/gpt-oss-120b) |
| Agent loop | Function calling with 5 tools |
| Retrieval (RAG) | sentence-transformers (all-MiniLM-L6-v2) |
| UI | Streamlit chat + catalog sidebar |
| Data | catalog.csv (14 products), policies.md |

**Tools:** `get_product_info`, `find_extreme`, `delivery_fee`, `price_with_vat`, `search_knowledge`

## 📁 Files
- `app.py` — Streamlit UI + agent loop + guardrails
- `shop_tools.py` — tool functions + RAG knowledge loading
- `catalog.csv` — product catalog (name, price ₦, stock, specs, warranty)
- `policies.md` — shop policies (delivery, warranty, returns)
- `requirements.txt` — dependencies

## 🚀 Run locally
```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key
streamlit run app.py
```

## 👤 Author
**Chetachukwu Sixtus Obiorah** — CS student, full-stack & AI developer
Part of the ATF AI Build Phase program.
