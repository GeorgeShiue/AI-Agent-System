import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

from graph import graph



# I am looking for a movie starring Keanu Reeves and the movie is about virtual reality.
async def main():
    config = {"recursion_limit": 50, "thread_id": "workflow123"}
    while True:
        user_input = input("Please enter your query (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break
    
        inputs = {"input": user_input}
        async for event in graph.astream(inputs, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(k, "\n", v)
                    if "response" in v:
                        print()
                        print("Final Response:", v["response"])
                    print()

asyncio.run(main())