from fastmcp import FastMCP 
import random
import json

mcp=FastMCP("simple calculation server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together.
    Args:
        a:First Number
        b:second nummber
    Returns:
        The sum of a and b.
    """
    return a + b
#Tool Generate a rando  number

@mcp.tool
def random_number(start: int=1, end: int=100) -> int:
    """ Genarate a random number between start and end.
    Args:
        start: The lower bound of the random number (default: 1).
        end: The upper bound of the random number (default: 100).
    Returns:
            A random integer between start and end.
    """
    return random.randint(start, end)

#Resource Server Information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about the server.
    Returns:
        A dictionary containing server information.
    """
    info= {
        "name": "Simple Calculation Server",
        "version": "1.0",
        "description": "A server that provides simple calculation tools and resources.",
        "tools":["add","random_number"],
        "author":"Bhawana Dhaka"
    }
    return json.dumps(info,indent=2)

if __name__=="__main__":    
    mcp.run(transport="http",host="0.0.0.0",port=8000)