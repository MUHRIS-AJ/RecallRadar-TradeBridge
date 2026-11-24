# RecallRadar + TradeBridge · Consumer recalls and macro trade research

### RecallRadar
Search the [US CPSC public recalls API](https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information) by consumer product name, returning recall number, title and source. A name match is **not proof your exact model is affected**.

```bash
python core.py RecallRadar "lamp"
```

### TradeBridge
Compare the World Bank's **exports of goods and services (current US$)** and **GDP (current US$)** indicators for two ISO country codes. This is macroeconomic context, **not** a product market forecast or actionable export recommendation.

```bash
python core.py TradeBridge "LK,IN"
```
Data: [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) and [Exports indicator](https://data.worldbank.org/indicator/NE.EXP.GNFS.CD).

### Run dashboard, tests, MCP
```bash
python dashboard.py --port 8765
python -m unittest discover -s tests -v
pip install -r requirements.txt
python server.py
```
Browser demo runs at http://localhost:8765. Optional FastMCP HTTP endpoint needs authentication before being made public.

All operations are read-only, evidence-linked, human-reviewed. The system does not send recall alerts or conduct international commerce.
