from langchain.memory import ConversationBufferMemory

# Initiate the memory buffer
memory = ConversationBufferMemory()
# execute a conversation...
# Get a list of the model and user messages
print(memory.chat_memory.messages)
# Get the chat history in string format
print(memory.buffer)
