import os
from typing import List, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent

from tools import movie_infos_search, movie_details_extract

load_dotenv()
api_key = os.getenv("API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

model = init_chat_model("gpt-4o-mini", model_provider="openai")
prompt = """
    Based on the plan steps provided by planner, please select the appropriate tool to use and provide the response of the plan step.
"""
tools = [movie_infos_search, movie_details_extract]
executor = create_react_agent(model, tools, prompt=prompt)



class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple step by step plan.  
This plan should involve individual tasks, that if executed correctly will yield the correct answer.  
Do not add any superfluous steps.  
The result of the final step should be the final answer.  
Make sure that each step has all the information needed – do not skip steps.

You can reference the following plan as an example:
    1. Generate a probable movie name based on user input  
    Goal: Extract or infer the most likely movie title the user is referring to from their natural language query.  
    Method: Apply semantic understanding, contextual reasoning, named entity recognition (NER), or prompted inference to transform the raw query into a clear movie name.

    2. Search IMDb and determine the correct movie based on search results  
    Goal: Use the inferred movie name from the previous step to perform an IMDb search and select the most semantically relevant result.  
    Method:  
    Use the movie_search(movie_name) tool to retrieve multiple search results  
    Compare result titles, release years, actors, and other metadata to identify the best match

    3. Retrieve detailed information about the selected movie from IMDb  
    Goal: Use the selected IMDb link to retrieve comprehensive movie metadata such as plot, cast, characters, directors, ratings, etc.  
    Method: Call the movie_metadata_search(imdb_url) tool

At each step, clearly output structured results such as:  
- Step 1 → movie_name: <string>  
- Step 2 → selected_movie_url: <IMDb URL>  
- Step 3 → metadata: <JSON object with fields such as title, plot, casts, etc.>      

If the provided movie is not what the user is looking for, start over and create a new plan by generating alternative possible movie names based on the user’s previous input and searching again.

Examples of mismatch conditions (triggering replan):  
- The plot returned is semantically inconsistent with the original user query.  
- None of the cast members match the ones mentioned by the user.  
- The title or year obviously contradicts contextual hints.
""",
        ),
        ("placeholder", "{messages}"),
    ]
)
planner = planner_prompt | ChatOpenAI(
    model="gpt-4o-mini", temperature=0
).with_structured_output(Plan)



class Response(BaseModel):
    """Response to user."""

    response: str

class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )

replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. 
If no more steps are needed and you can return to the user, then respond with that. 
If you need more information from the user to complete the task, then respond with that.
Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
"""
)
replanner = replanner_prompt | ChatOpenAI(
    model="gpt-4o", temperature=0
).with_structured_output(Act)