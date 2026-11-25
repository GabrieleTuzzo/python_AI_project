import asyncio
from collections.abc import Callable
from typing import Any

from mcp import Client
from mcp.types import CallToolResult, TextContent
from ollama import AsyncClient

from be.mcp_server import mcp as notes_mcp
from be.prompts import SYSTEM_PROMPT

MODEL = "qwen2.5:3b"


def make_ollama_tools(mcp_tools):
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]


def tool_result_text(result: CallToolResult) -> str:
    return "\n".join(
        item.text
        for item in result.content
        if isinstance(item, TextContent)
    ) or "The tool returned no text."


def confirm_delete_in_terminal(note_id: str) -> bool:
    answer = input(f"Confermi l'eliminazione della nota {note_id}? (s/n): ")
    return answer.strip().casefold() == "s"


async def execute_tool_call(
    mcp_client: Client,
    name: str,
    arguments: dict[str, Any],
    confirm_delete: Callable[[str], bool],
) -> str:
    if name == "delete_note":
        note_id = str(arguments.get("note_id", "sconosciuto"))
        if not confirm_delete(note_id):
            return "Eliminazione annullata dall'utente."

    result = await mcp_client.call_tool(name, arguments)
    return tool_result_text(result)


async def run_chat() -> None:
    async with Client(notes_mcp) as mcp_client:
        tool_list = await mcp_client.list_tools()
        tools = make_ollama_tools(tool_list.tools)

        async with AsyncClient() as ollama:
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ]

            while True:
                prompt = input("Tu (oppure /q per uscire): ").strip()
                if prompt.casefold() in {"/q", "quit", "exit"}:
                    break
                if not prompt:
                    continue

                messages.append({"role": "user", "content": prompt})

                for _ in range(5):
                    response = await ollama.chat(
                        model=MODEL,
                        messages=messages,
                        tools=tools,
                    )
                    messages.append(response.message)

                    if not response.message.tool_calls:
                        print(f"Bot: {response.message.content}")
                        break

                    for call in response.message.tool_calls:
                        name = call.function.name
                        arguments = call.function.arguments
                        messages.append({
                            "role": "tool",
                            "tool_name": name,
                            "content": await execute_tool_call(
                                mcp_client,
                                name,
                                arguments,
                                confirm_delete_in_terminal,
                            ),
                        })
                else:
                    print("Raggiunto il limite di chiamate agli strumenti per questa richiesta.")


def main() -> None:
    asyncio.run(run_chat())


if __name__ == "__main__":
    main()