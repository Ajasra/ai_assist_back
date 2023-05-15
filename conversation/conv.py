import os
from dotenv import load_dotenv


from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferMemory, ConversationSummaryMemory, \
    ConversationBufferWindowMemory
from langchain import PromptTemplate


load_dotenv()
openai_api = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=.0, model_name="gpt-3.5-turbo", openai_api_key=openai_api)

conversations = []
memories = []

def get_agent_response(prompt, conversation_id, debug):


    _DEFAULT_TEMPLATE = "Context information is below. \n" \
                        "-----------\n"\
                        "context_str\n"\
                        "{history}\n"\
                        "\n---------\n"\
                        "- Given the context information answer the following question in few paragraphs"\
                        "- If you don't know the answer, say you dont know"\
                        "- Always answer in the format:"\
                        "ANSWER: <your answer>\n"\
                        "FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>\n"\
                        "SOURCE: <do not make up source, give the page or the chapter from where information extracted>"\
                        "QUESTION: {input}\n"



    PR_TEMPLATE = PromptTemplate(
        input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
    )

    if conversation_id >= len(conversations) or len(conversations) == 0:

        memory = ConversationBufferWindowMemory(
            memory_key="history",
            input_key="input",
            k=1
        )
        memories.append(memory)
        conversations.append(ConversationChain(
            llm=llm,
            verbose=True,
            memory=memory,
            prompt=PR_TEMPLATE
        ))
        conversation_id = len(conversations) - 1
        cur_conversation = conversations[conversation_id]
    else:
        cur_conversation = conversations[conversation_id]

    result = cur_conversation.run(prompt)

    if debug:
        print(result)

    return result


def get_conversation_count():
    """Get conversation count.

    Returns:
        int: Conversation count.
    """

    return len(conversations)