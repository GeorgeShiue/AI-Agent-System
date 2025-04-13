import asyncio
import operator
from typing import Annotated, List, Tuple

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents import executor, planner, replanner, Response

class PlanExecute(MessagesState):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str



async def execute_step(state: PlanExecute):
    user_input = state["input"]
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""User Input: {user_input}\n\n 
For the following plan:
{plan_str}\n\nYou are tasked with executing step {1}, {task}."""
    agent_response = await executor.ainvoke(
        {"messages": [("user", task_formatted)]},
        config={"configurable": {"thread_id": "executor123"}}
    )
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }

async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    
    if "response" in state and state["response"]:
        return {"plan": plan.steps, "response": ""}
    
    return {"plan": plan.steps}

async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}

def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"
    


workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

# From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    ["agent", END],
)

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
memeory = MemorySaver()
app = workflow.compile(checkpointer=memeory)



async def main():
    config = {"recursion_limit": 50, "thread_id": "workflow123"}
    while True:
        # 提示使用者輸入查詢
        user_input = input("Please enter your query (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break
        
        inputs = {"input": user_input}
        async for event in app.astream(inputs, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(v)
                    if "response" in v:
                        print(v["response"])

asyncio.run(main())

# Terminator: I am looking for a movie that a robot pretending to be a human and trying to assassinate the main character.
# The Avengers: I am looking for a movie that starring Robert Downey Jr., Chris Evans, and Scarlett Johansson.
# The Matrix: I am looking for a movie starring Keanu Reeves and the movie is about virtual reality.