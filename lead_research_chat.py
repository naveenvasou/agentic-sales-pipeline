from agents import create_lead_generation_agent

def main():
    """
    The main function to run the interactive lead generation agent.
    """
    print("🤖 Lead Generation Agent is ready.")
    print("Type 'exit' or 'quit' to end the session.")
    
    # Create the agent executor instance
    agent_executor = create_lead_generation_agent()

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            # Invoke the agent with the user's input
            response = agent_executor.invoke({"input": user_input})
            
            # Print the final answer from the agent
            print("\nAgent:")
            print(response["output"])
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()