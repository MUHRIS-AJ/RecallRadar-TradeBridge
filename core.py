"""RecallRadar: official recalls. TradeBridge: World Bank macro trade indicators."""
from __future__ import annotations
import re
from transport import request_json, SourceError

SERVICES=["RecallRadar","TradeBridge"]
CPSC="https://www.saferproducts.gov/RestWebServices/Recall"
FDA="https://api.fda.gov/food/enforcement.json"
WORLD="https://api.worldbank.org/v2/country/"

def food_recalls(product: str):
    """Search official openFDA food enforcement records (food:<name>)."""
    if not re.fullmatch(r"[\w .,\-]{2,80}", product, re.UNICODE):
        raise ValueError("Use a food item name of 2–80 characters.")
    data=request_json(FDA, params={"search":'product_description:"'+product.strip()+'"', "limit":20})
    records=data.get("results") or []
    if not isinstance(records,list):
        raise SourceError("openFDA returned an unexpected response.")
    rows=[]
    for e in records[:20]:
        number=e.get("recall_number")
        if not number:continue
        rows.append({"recall_number":number, "title":e.get("product_description"),
                     "reason":e.get("reason_for_recall"),"recall_date":e.get("report_date"),
                     "status":e.get("status"),"official_provider":"US FDA",
                     "url":"https://open.fda.gov/apis/food/enforcement/",
                     "product_match_requires_review":True})
    return {"project":"RecallRadar","mode":"FDA food enforcement","query":product,
            "count":len(rows),"recalls":rows,"source":FDA,
            "agents":["Discover: openFDA food enforcement","Analyze: product description",
            "Verify: agency and recall number","Report: source-linked records"],
            "limitations":["US FDA reports are not a complete global recall registry.",
                "A matching name does not prove a specific package or lot is affected.",
                "Consult official FDA notices and product identifiers before acting."]}

def recalls(product: str):
    if not isinstance(product,str) or not 2 <= len(product.strip()) <= 90 or not re.fullmatch(r"[\w .,\-]+",product,re.UNICODE):
        raise ValueError("Use a short product name containing letters, numbers and basic punctuation.")
    # Source Agent: US CPSC public product recall database, not a medical diagnosis.
    records=request_json(CPSC,params={"ProductName":product.strip(),"format":"json"})
    if isinstance(records,dict):
        records=records.get("recalls",records.get("results",[]))
    if not isinstance(records,list):
        raise SourceError("CPSC returned an unexpected JSON response.")
    hits=[]
    for record in records[:20]:
        if not isinstance(record,dict):continue
        number=record.get("RecallNumber") or record.get("RecallID")
        if not number:continue
        products=record.get("Products") or []
        titles=[p.get("Name","") for p in products if isinstance(p,dict)]
        hits.append({"recall_number":str(number),"title":record.get("Title") or "; ".join(titles),
                     "recall_date":record.get("RecallDate"),
                     "url":record.get("URL") or "https://www.cpsc.gov/Recalls",
                     "official_provider":"US Consumer Product Safety Commission",
                     "product_match_requires_review":True})
    return {"project":"RecallRadar","query":product,"count":len(hits),"recalls":hits,
        "source":CPSC,"agents":["Discover: CPSC recall records","Analyze: product title","Verify: recall ID and provider","Report: human-checkable notifications"],
        "limitations":["Searching a product name alone cannot confirm your exact model or batch.",
                       "Consult the official recall notice for affected models and remedies.",
                       "Covers US CPSC public recalls; no automated monitoring or notifications."]}

def _latest(series):
    if not isinstance(series,list) or len(series)<2 or not isinstance(series[1],list):
        raise SourceError("World Bank returned unexpected indicator data.")
    for entry in series[1]:
        if entry.get("value") is not None:
            return {"year":entry.get("date"),"value_usd":entry["value"]}
    return {"year":None,"value_usd":None}

def trade(countries: str):
    """Compare macro export and GDP indicators; NOT a recommendation or market demand forecast."""
    codes=[x.strip().upper() for x in countries.split(",")]
    if len(codes)!=2 or len(set(codes))!=2 or any(not re.fullmatch(r"[A-Z]{2,3}",x) for x in codes):
        raise ValueError("Use two distinct ISO country codes, e.g. LK,IN or USA,GBR.")
    result=[]
    for code in codes:
        indicators={}
        for indicator in ("NE.EXP.GNFS.CD","NY.GDP.MKTP.CD"):
            url=WORLD+code+"/indicator/"+indicator
            data=request_json(url,params={"format":"json","per_page":10,"mrv":10})
            indicators[indicator]=_latest(data)
        result.append({"country":code,"latest_exports_of_goods_and_services":indicators["NE.EXP.GNFS.CD"],
                       "latest_gdp":indicators["NY.GDP.MKTP.CD"],
                       "source_url":"https://data.worldbank.org/country/"+code.lower()})
    return {"project":"TradeBridge","countries":codes,"data":result,
        "source":"World Bank World Development Indicators",
        "indicator_urls":["https://data.worldbank.org/indicator/NE.EXP.GNFS.CD",
                          "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD"],
        "agents":["Discover: World Bank indicator API","Analyze: latest non-null annual values","Verify: country and source indicator","Report: side-by-side comparison"],
        "limitations":["Macroeconomic indicators are not demand for a particular product.",
                       "Different available years may make direct comparisons misleading.",
                       "No import tariffs, country regulations, HS codes or buyer demand included."]}

def run(query:str,service:str="RecallRadar"):
    if service=="RecallRadar":
        return food_recalls(query[5:].strip()) if query.lower().startswith("food:") else recalls(query)
    if service=="TradeBridge":return trade(query)
    raise ValueError("Unknown service.")

if __name__=="__main__":
    import argparse,json
    ap=argparse.ArgumentParser()
    ap.add_argument("service",choices=SERVICES);ap.add_argument("query")
    a=ap.parse_args()
    try:print(json.dumps(run(a.query,a.service),indent=2))
    except (ValueError,SourceError) as exc:ap.exit(2,str(exc)+"\n")
