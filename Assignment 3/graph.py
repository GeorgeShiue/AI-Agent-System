import operator
import shutil
from typing import Annotated, List, Tuple

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.documents import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma

from agents import planner, executor, replanner, Response



class PlanExecute(MessagesState):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str



shutil.rmtree("./plan_documents_db", ignore_errors=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

plan_docs_vector_store = Chroma(
    collection_name="plan_documents",
    embedding_function=embeddings,
    persist_directory="./plan_documents_db",
)

plan_docs = []

def save_plan_docs(user_input: str, plan: List[str]):
    plan_str = "\n".join(plan)

    doc = Document(
        page_content=(
            user_input
        ),
        metadata={
            "user_input": user_input,
            "plan": plan_str,
        }
    )

    plan_docs.append(doc)
    plan_docs_vector_store.add_documents([doc])

    print("Successfully saved the plan documents to the vector store.")



def retrieve_plan_doc(state: PlanExecute):
    user_input = state["input"]
    results = plan_docs_vector_store.similarity_search_with_score(user_input, k=1)
    
    if not results:
        print("No plan found in the vector store.")
        return {"plan": None}
    
    score = results[0][1]
    if score > 0.5:
        print("No plan found in the vector store.")
        plan = None
    else:
        print("Successfully retrieved the plan from the vector store. Socre:", score)
        plan = results[0][0].metadata["plan"].split("\n")
    
    return {"plan": plan}

def should_plan(state: PlanExecute):
    if not state["plan"]:
        return "planner"
    else:
        return "executor"
    
async def plan_step(state: PlanExecute):
    # * 傳入上次執行結果
    if "response" in state and state["response"]:
        plan = await planner.ainvoke({"messages": [
            ("user", "Last Respone: " + state["response"]),
            ("user", f"User Input: {state["input"]}"),
        ]})

        save_plan_docs(state["input"], plan.steps)

        return {"plan": plan.steps, "response": ""}
    
    plan = await planner.ainvoke({"messages": [
        ("user", f"User Input: {state["input"]}"),
    ]})

    save_plan_docs(state["input"], plan.steps)

    return {"plan": plan.steps}

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
        return "executor"
    


graph_builder = StateGraph(PlanExecute)

graph_builder.add_node("retriever", retrieve_plan_doc)
graph_builder.add_node("planner", plan_step)
graph_builder.add_node("executor", execute_step)
graph_builder.add_node("replanner", replan_step)

graph_builder.add_edge(START, "retriever")
graph_builder.add_conditional_edges(
    "retriever",
    should_plan,
    ["planner", "executor"],
)
graph_builder.add_edge("planner", "executor")
graph_builder.add_edge("executor", "replanner")
graph_builder.add_conditional_edges(
    "replanner",
    should_end,
    ["executor", END],
)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)