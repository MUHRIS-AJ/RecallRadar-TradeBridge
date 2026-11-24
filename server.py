from fastmcp import FastMCP
from core import recalls,trade
mcp=FastMCP("MUHRIS RecallRadar and TradeBridge")
@mcp.tool
def search_product_recalls(product_name:str)->dict:
    """Find official CPSC product recalls with identifiers and verification warnings."""
    return recalls(product_name)
@mcp.tool
def compare_countries_macro_trade(first_country:str,second_country:str)->dict:
    """Compare official World Bank GDP/export indicators for two ISO country codes."""
    return trade(first_country+","+second_country)
if __name__=="__main__":mcp.run()
