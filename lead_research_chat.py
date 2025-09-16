from agents import create_lead_generation_agent
import logging
import json
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from typing import Any

logging.basicConfig(filename='agent_run.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

trace_logger = logging.getLogger("agent_trace")
trace_logger.setLevel(logging.INFO)
trace_handler = logging.FileHandler("agent_trace.log")
trace_handler.setLevel(logging.INFO)
trace_formatter = logging.Formatter("%(message)s")
trace_handler.setFormatter(trace_formatter)
trace_logger.addHandler(trace_handler)

class AgentTraceCallbackHandler(BaseCallbackHandler):
    """Logs the agent's thoughts and actions to a separate file."""
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        log_entry = {
            "stage": "agent_action",
            "thought": action.log.strip(),
            "tool": action.tool,
            "tool_input": action.tool_input
        }
        trace_logger.info(json.dumps(log_entry, indent=2) + ",")

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        log_entry = {
            "stage": "tool_output",
            "tool_output": output
        }
        trace_logger.info(json.dumps(log_entry, indent=2) + ",")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        log_entry = {
            "stage": "agent_finish",
            "final_answer": finish.return_values.get('output')
        }
        trace_logger.info(json.dumps(log_entry, indent=2))
        
def main():
    """
    The main function to run the interactive lead generation agent.
    """
    print("🤖 Lead Generation Agent is ready.")
    print("Type 'exit' or 'quit' to end the session.")
    
    logger.info("Application started. Initializing lead generation agent.")
    try:
        agent_executor = create_lead_generation_agent()
        logger.info("Agent executor instance created successfully.")
    except Exception as e:
        logger.critical(f"Failed to create agent executor: {e}. Exiting.")
        print("An error occurred during agent initialization. Check the logs.")
        return

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            logger.info("Invoking the agent executor.")
            response = agent_executor.invoke({"input": user_input}, callbacks=[AgentTraceCallbackHandler()])
            logger.info("Agent execution complete. Output received.")
            print("\nAgent:")
            print(response["output"])
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()