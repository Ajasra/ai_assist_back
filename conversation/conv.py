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