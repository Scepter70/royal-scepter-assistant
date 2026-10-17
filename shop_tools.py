_TOOLS_SCHEMA_JSON = "[{\"type\":\"function\",\"function\":{\"name\":\"get_product_info\",\"description\":\"Get exact price, stock, specs and warranty for one product by partial name.\",\"parameters\":{\"type\":\"object\",\"properties\":{\"name\":{\"type\":\"string\"}},\"required\":[\"name\"]}}},{\"type\":\"function\",\"function\":{\"name\":\"find_extreme\",\"description\":\"Find the cheapest (min) or most expensive (max) product in a category.\",\"parameters\":{\"type\":\"object\",\"properties\":{\"category\":{\"type\":\"string\",\"enum\":[\"Laptop\",\"Smartphone\"]},\"mode\":{\"type\":\"string\",\"enum\":[\"min\",\"max\"]}},\"required\":[\"category\",\"mode\"]}}},{\"type\":\"function\",\"function\":{\"name\":\"delivery_fee\",\"description\":\"Estimate delivery fee. Free within Lagos for orders of 500,000 Naira or more.\",\"parameters\":{\"type\":\"object\",\"properties\":{\"area\":{\"type\":\"string\",\"enum\":[\"lagos-mainland\",\"lagos-island\",\"outside-lagos\"]},\"order_total\":{\"type\":\"number\"}},\"required\":[\"area\",\"order_total\"]}}},{\"type\":\"function\",\"function\":{\"name\":\"price_with_vat\",\"description\":\"Price including 7.5% Nigerian VAT.\",\"parameters\":{\"type\":\"object\",\"properties\":{\"name\":{\"type\":\"string\"}},\"required\":[\"name\"]}}},{\"type\":\"function\",\"function\":{\"name\":\"search_knowledge\",\"description\":\"Semantic search over catalog and shop policies.\",\"parameters\":{\"type\":\"object\",\"properties\":{\"query\":{\"type\":\"string\"}},\"required\":[\"query\"]}}}]"
import pandas as pd
import numpy as np
import re, json
from sentence_transformers import SentenceTransformer

MODEL = "openai/gpt-oss-120b"

def load_knowledge(catalog_csv_path, policies_path):
    catalog = pd.read_csv(catalog_csv_path)
    with open(policies_path) as f:
        policies = f.read()
    docs = []
    for _, r in catalog.iterrows():
        t = str(r["name"]) + " (" + str(r["category"]) + "): " + format(int(r["price_naira"]), ",") + " Naira. Specs: " + str(r["specs"]) + ". Stock: " + str(r["stock"]) + " available. Warranty: " + str(r["warranty_months"]) + " months."
        docs.append({"type": "product", "text": t})
    for section in policies.split("\n\n## ")[1:]:
        title = section.split("\n")[0]
        body = section[section.find("\n")+1:].strip() if "\n" in section else ""
        docs.append({"type": "policy", "text": title + ": " + body})
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedder.encode([d["text"] for d in docs], normalize_embeddings=True)
    return catalog, docs, embeddings, embedder

def make_tools(catalog, docs, embeddings, embedder):
    def tool_get_product_info(name):
        m = catalog[catalog["name"].str.lower().str.contains(str(name).lower())]
        if len(m) == 0:
            return {"error": "Product not found in catalog"}
        r = m.iloc[0]
        return {"name": r["name"], "price_naira": int(r["price_naira"]), "stock": int(r["stock"]), "specs": str(r["specs"]), "warranty_months": int(r["warranty_months"])}
    def tool_find_extreme(category, mode):
        m = catalog[catalog["category"].str.lower() == str(category).lower()]
        if len(m) == 0:
            return {"error": "Category not found"}
        r = m.loc[m["price_naira"].idxmin() if str(mode) == "min" else m["price_naira"].idxmax()]
        return {"name": r["name"], "price_naira": int(r["price_naira"]), "category": str(r["category"])}
    def tool_delivery_fee(area, order_total):
        fees = {"lagos-mainland": 3500, "lagos-island": 4000, "outside-lagos": 5000}
        fee = fees.get(str(area).lower())
        if fee is None:
            return {"error": "Unknown area."}
        total = float(order_total)
        free = total >= 500000 and str(area).lower() != "outside-lagos"
        return {"delivery_fee_naira": 0 if free else fee, "free_delivery": bool(free)}
    def tool_price_with_vat(name):
        info = tool_get_product_info(name)
        if "error" in info:
            return info
        vat = int(round(info["price_naira"] * 0.075))
        return {"name": info["name"], "base_price_naira": info["price_naira"], "vat_naira": vat, "total_with_vat_naira": info["price_naira"] + vat}
    def tool_search_knowledge(query):
        q_emb = embedder.encode([str(query)], normalize_embeddings=True)[0]
        best = np.argsort(-(embeddings @ q_emb))[:4]
        return {"results": [docs[i]["text"] for i in best]}
    return {"get_product_info": tool_get_product_info, "find_extreme": tool_find_extreme, "delivery_fee": tool_delivery_fee, "price_with_vat": tool_price_with_vat, "search_knowledge": tool_search_knowledge}

TOOLS_SCHEMA = json.loads(_TOOLS_SCHEMA_JSON)
