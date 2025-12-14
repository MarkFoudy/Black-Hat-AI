#!/usr/bin/env python3
"""
Memory buffer and reflection demonstration.

From Listing 2.9 in Black Hat AI.

Demonstrates:
- LangChain conversation memory
- Accessing chat history
- Buffer management
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    """Run memory buffer demonstration."""
    print("=" * 60)
    print("Example 4: Memory Buffer & Reflection")
    print("=" * 60)
    print()

    try:
        from langchain.memory import ConversationBufferMemory
    except ImportError:
        print("ERROR: LangChain not installed")
        print("Install with: pip install langchain")
        return 1

    # Initialize memory buffer
    print("Initializing conversation memory buffer...")
    memory = ConversationBufferMemory()

    # Simulate a conversation
    print("\nSimulating agent conversation...")
    print("-" * 60)

    # Add some messages
    memory.chat_memory.add_user_message("What hosts should I scan first?")
    memory.chat_memory.add_ai_message(
        "I recommend starting with high-value targets like admin interfaces."
    )
    memory.chat_memory.add_user_message("Check if admin.example.com is reachable")
    memory.chat_memory.add_ai_message("admin.example.com is reachable via ping.")

    # Display chat history as structured messages
    print("\n1. Structured Message History:")
    print("-" * 60)
    for i, msg in enumerate(memory.chat_memory.messages, 1):
        role = "User" if hasattr(msg, "type") and msg.type == "human" else "AI"
        print(f"{i}. [{role}] {msg.content}")

    # Display chat history as formatted string
    print("\n2. Formatted Buffer (String):")
    print("-" * 60)
    print(memory.buffer)

    # Demonstrate memory persistence across turns
    print("\n3. Adding More Context:")
    print("-" * 60)
    memory.chat_memory.add_user_message("What did we just check?")
    memory.chat_memory.add_ai_message(
        "We checked admin.example.com and confirmed it's reachable."
    )

    print("Updated buffer:")
    print(memory.buffer)

    print("\n" + "=" * 60)
    print("Example completed.")
    print()
    print("Key Takeaways:")
    print("- memory.chat_memory.messages: List of message objects")
    print("- memory.buffer: Formatted string representation")
    print("- Memory persists across conversation turns")
    print("- Critical for agent reflection and learning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
