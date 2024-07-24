from crewai import Agent
import requests
from bs4 import BeautifulSoup

def web_scraping_tool(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract and return relevant data
    return soup.get_text()

class CustomAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tools = {
            'web_scraping_tool': web_scraping_tool,
            # Add other tools here
        }

    def use_tool(self, tool_name, *args, **kwargs):
        if tool_name in self.tools:
            return self.tools[tool_name](*args, **kwargs)
        else:
            raise ValueError(f"Tool {tool_name} not found")

# Now when defining your agent:
news_aggregator = CustomAgent(
    name="News Aggregator",
    role="Responsible for gathering and selecting top news stories",
    goal="Collect and prioritize the most important current news stories",
    backstory="An experienced journalist with a keen eye for important stories",
    tools=["web_scraping_tool"]
)