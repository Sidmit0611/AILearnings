import sys
import traceback

from agent.graph_updated import agent

def main():
    parser = argparse.ArgumentParser(description="Run engineering project planner.")
    parser.add_argument("--recursion-limit", "-r", type=int, default=100, help="Set the recursion limit for coder agent (default: 100).")

    args = parser.parse_args()

    try:
        user_prompt = input("Enter the project you want to create: ")
        result = agent.invoke(
            {
                "user_prompt": user_prompt
            },
            {
                "recursion_limit": args.recursion_limit
            }
        )
        print("Final Result:", result)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print("\nAn error occurred:")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()