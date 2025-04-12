import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools import movie_infos_search, movie_metadata_extract

load_dotenv()
api_key = os.getenv("API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

model = init_chat_model("gpt-4o-mini", model_provider="openai")

prompt = """
    Based on user's query, please perform the following steps:
    1. Generate the name of the movie that the user is looking for.
    2. Pass the name of the movie to movie_search tool to get the movies from IMDb search results.
        Note: 
            Do not directly pass some keywords inside user's query to the movie_search tool.
    3. Inspect the search results and select the one movie that you think is the most relevant to the user's query.
    4. Pass the link of the movie that you selected to movie_metadata_search tool to get the movie title, plot, casts, characters, directors, writers, rating, popularity.
    5. Based on the movie metadata, generate the final response to the user.
    """

memory = MemorySaver()
tools = [movie_infos_search, movie_metadata_extract]
agent_executor = create_react_agent(model, tools, checkpointer=memory, prompt=prompt)

# Terminator 2: I am looking for a movie that a robot pretending to be a human and trying to assassinate the main character. The mvoie is the second installment in a series.
# The Avengers: I am looking for a movie that starring Robert Downey Jr., Chris Evans, and Scarlett Johansson.
# The Matrix: I am looking for a movie starring Keanu Reeves and the movie is about virtual reality.
movie_infos = []
query = "I am looking for a movie starring Keanu Reeves and the movie is about virtual reality."

config = {"configurable": {"thread_id": "abc123"}}
for step in agent_executor.stream(
    {"messages": [HumanMessage(content=query)]},
    config,
    stream_mode="values",
):
    step["messages"][-1].pretty_print()