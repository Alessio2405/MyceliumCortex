import sys
import asyncio
import argparse
import logging

logger = logging.getLogger("myceliumcortex.cli")

def main():
    parser = argparse.ArgumentParser(prog="myceliumcortex")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("chat")
    msgp = sub.add_parser("message")
    msgp.add_argument("text")
    sub.add_parser("status")
    sub.add_parser("config")

    # Agent management
    agentp = sub.add_parser("agent")
    agent_sub = agentp.add_subparsers(dest="agent_cmd")
    addp = agent_sub.add_parser("add")
    addp.add_argument("agent_id")
    addp.add_argument("class_path")
    listp = agent_sub.add_parser("list")
    enablep = agent_sub.add_parser("enable")
    enablep.add_argument("agent_id")
    disablep = agent_sub.add_parser("disable")
    disablep.add_argument("agent_id")
    args = parser.parse_args()

    # Best-effort: try to reuse existing main module from src.main
    try:
        from src.main import MiniClawAssistant

        assistant_cls = MiniClawAssistant
    except Exception:
        assistant_cls = None

    if args.cmd == "chat":
        if assistant_cls:
            asyncio.run(assistant_cls().interactive_chat())
        else:
            print("Interactive chat requires src.main.MiniClawAssistant. None found.")
    elif args.cmd == "message":
        if assistant_cls:
            asyncio.run(assistant_cls().chat(args.text))
        else:
            print("Single-message mode requires src.main.MiniClawAssistant. None found.")
    elif args.cmd == "status":
        print("MyceliumCortex CLI: status unknown (run API gateway for full status)")
    elif args.cmd == "agent":
        # Use host manager via API if available
        if args.agent_cmd == "add":
            agent_id = args.agent_id
            class_path = args.class_path
            import json, requests
            payload = {"class": class_path}
            try:
                r = requests.post("http://127.0.0.1:8000/v1/agents", json={"agent_id": agent_id, "config": payload})
                print(r.status_code, r.text)
            except Exception as e:
                print("Failed to call API. Is the server running?", e)
        elif args.agent_cmd == "list":
            import requests
            try:
                r = requests.get("http://127.0.0.1:8000/v1/agents")
                print(r.json())
            except Exception as e:
                print("Failed to call API. Is the server running?", e)
        elif args.agent_cmd == "enable":
            import requests
            try:
                r = requests.post(f"http://127.0.0.1:8000/v1/agents/{args.agent_id}/enable")
                print(r.status_code, r.text)
            except Exception as e:
                print("Failed to call API. Is the server running?", e)
        elif args.agent_cmd == "disable":
            import requests
            try:
                r = requests.post(f"http://127.0.0.1:8000/v1/agents/{args.agent_id}/disable")
                print(r.status_code, r.text)
            except Exception as e:
                print("Failed to call API. Is the server running?", e)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
