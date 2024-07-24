from crewai import Agent, Task, Crew, Process

# Define the agents

news_aggregator = Agent(
    name="News Aggregator",
    role="Responsible for gathering and selecting top news stories",
    goal="Collect and prioritize the most important current news stories",
    backstory="An experienced journalist with a keen eye for important stories",
    tools=["web_scraping_tool", "news_api_tool"]
)

content_enhancer = Agent(
    name="Content Enhancer",
    role="Expands and provides context to news stories",
    goal="Create comprehensive and engaging content from raw news data",
    backstory="A skilled writer and researcher with a broad knowledge base",
    tools=["text_generation_model", "fact_checking_tool"]
)

visual_creator = Agent(
    name="Visual Creator",
    role="Generates relevant images and infographics for news stories",
    goal="Create compelling visual content to accompany news stories",
    backstory="An AI artist with a journalistic eye for impactful visuals",
    tools=["image_generation_model", "data_visualization_tool"]
)

audio_producer = Agent(
    name="Audio Producer",
    role="Creates audio narration and ambient sounds for news stories",
    goal="Produce immersive audio experiences for news content",
    backstory="An audio engineer with experience in news broadcasting",
    tools=["text_to_speech_model", "audio_editing_tool"]
)

content_assembler = Agent(
    name="Content Assembler",
    role="Combines all elements into a cohesive multimedia package",
    goal="Create engaging, multi-format news experiences",
    backstory="A multimedia expert with a background in digital journalism",
    tools=["content_management_system", "web_publishing_tool"]
)

# Define the tasks

task1 = Task(
    description="Gather and select top news stories for immersive treatment",
    agent=news_aggregator
)

task2 = Task(
    description="Enhance and expand selected news stories with context and additional perspectives",
    agent=content_enhancer
)

task3 = Task(
    description="Generate relevant visual content for the enhanced news stories",
    agent=visual_creator
)

task4 = Task(
    description="Produce audio narration and ambient sounds for the news stories",
    agent=audio_producer
)

task5 = Task(
    description="Assemble all components into a cohesive multimedia news package",
    agent=content_assembler
)

# Create the crew
newsverse_crew = Crew(
    agents=[news_aggregator, content_enhancer, visual_creator, audio_producer, content_assembler],
    tasks=[task1, task2, task3, task4, task5],
    process=Process.sequential
)

# Run the crew
result = newsverse_crew.kickoff()

print(result)