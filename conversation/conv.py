import os

from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain.chains.summarize import load_summarize_chain

from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, \
    MessagesPlaceholder
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_helper import DocumentsToStr
from cocroach_utils.db_history import add_history, get_history_for_conv
from cocroach_utils.db_docs import update_doc_summary_by_id, update_doc_steps_by_id, get_doc_by_id
from conversation.conv_helper import get_conv_id, format_response, moderation

from vectordb.vectordb import get_embedding_model
from vectordb.vectordb import get_loader

load_dotenv()
model_name = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k"]
persist_directory = './db'

llm = ChatOpenAI(temperature=.0, model_name=model_name[0], verbose=True, model_kwargs={"stream": False})


def get_doc_summary(file, doc_id, chunk_size=2048, chunk_overlap=64):
    if file.filename == '':
        return {
            "status": "error",
            "message": "No file selected"
        }
    filename = f"./data/{file.filename}"
    loader = get_loader(filename)
    documents = loader.load()
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                      encoding_name="cl100k_base")
    docs = text_splitter.split_documents(documents)

    prompt_template = """Write a concise and condensed summary of the following:

    {text}

    CONCISE SUMMARY:"""

    prompttemplate = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(llm, chain_type="map_reduce", return_intermediate_steps=True,
                                 map_prompt=prompttemplate, combine_prompt=prompttemplate)

    try:
        summary = chain({"input_documents": docs}, return_only_outputs=True)
        intermediate_steps = summary['intermediate_steps']
        intermediate_steps = "\n".join(intermediate_steps)
        result = summary['output_text']
        update_doc_summary_by_id(doc_id, result)
        try:
            update_doc_steps_by_id(doc_id, intermediate_steps)
        except Exception as e:
            print("Error in updating steps: ", e)

        return {
            "status": "success",
            "message": "File summary",
            "data": {
                "summary": result,
                "steps": intermediate_steps
            }
        }

    except Exception as e:
        save_error(e)
        return {
            "status": "error",
            "message": "Error in getting summary",
        }


def get_simple_response(prompt, conv_id, user_id, memory=10):
    """
    Get a simple response from the model
    :param memory:
    :param user_id:
    :param prompt:
    :param conv_id:
    :return:
    """

    cur_conv = get_conv_id(conv_id, user_id, 0)
    if cur_conv == -1:
        return {
            "status": "error",
            "message": "Conversation not found or can't be created",
            "conversation_id": conv_id
        }

    template = """You are a chatbot having a conversation with a human.

    {chat_history}
    Human: {human_input}
    Chatbot:"""

    prompt_template = PromptTemplate(
        input_variables=["chat_history", "human_input"], template=template
    )
    memory_obj = ConversationBufferMemory(memory_key="chat_history")

    if memory != -1:
        # get history from db
        history = get_history_for_conv(cur_conv, 2)
        if history is not None:
            # from last to first
            history.reverse()
            for hist in history:
                memory_obj.save_context(
                    {"question": hist["prompt"]},
                    {"output": hist["answer"]})

    chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        verbose=True,
        memory=memory_obj,
    )

    # Notice that we just pass in the `question` variables - `chat_history` gets populated by memory
    # chain({"question": prompt})

    # system = PromptTemplate(
    #     template="You are a helpful assistant that translates {input_language} to {output_language}.",
    #     input_variables=["input_language", "output_language"],
    # )
    # system = PromptTemplate(
    #     template="",
    #     input_variables=[],
    # )
    # system_message_prompt = SystemMessagePromptTemplate(prompt=system)
    # human_template = "{text}"
    # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    #
    # chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    # chain = LLMChain(llm=llm, prompt=chat_prompt)

    try:
        response = chain.predict(human_input=prompt)
        hist_id = add_history(cur_conv, prompt, response, "")
    except Exception as e:
        save_error(e)
        return {
            "status": "error",
            "message": str(e),
            "conversation_id": cur_conv
        }

    return {
        "status": "success",
        "message": "Agent response",
        "data": {
            "response": response,
            "follow_up_questions": "",
            "source": "",
            "conversation_id": cur_conv,
            "history_id": hist_id
        }
    }


def get_response_over_doc(prompt, conv_id, doc_id, user_id, memory):
    if doc_id is not None:

        user_prompt = prompt
        history = []

        index_dir = os.path.join(persist_directory, str(doc_id))
        embeddings = get_embedding_model()
        docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)

        cur_conv = get_conv_id(conv_id, user_id, doc_id)
        if cur_conv == -1:
            return {
                "status": "error",
                "message": "Conversation not found or can't be created",
                "conversation_id": conv_id
            }

        _DEFAULT_TEMPLATE = """Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
                            If you don't know the answer, reply "NONE".
                            Always reply in the Markdown format.
                            =========
                            ------
                            <ctx>
                            {context}
                            </ctx>
                            ------
                            <hs>
                            {history}
                            </hs>
                            ------
                            {question}
                            Answer: """

        promptTmp = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=_DEFAULT_TEMPLATE,
        )

        retriever = docsearch.as_retriever()

        memory_obj = ConversationBufferMemory(
            memory_key="history",
            input_key="question")

        if memory != -1:
            # get history from db
            history = get_history_for_conv(cur_conv, 2)
            if history is not None:
                # from last to first
                history.reverse()
                for hist in history:
                    memory_obj.save_context(
                        {"question": hist["prompt"]},
                        {"output": hist["answer"]}
                    )

        cur_conversation = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=False,
            chain_type_kwargs={
                "prompt": promptTmp,
                "memory": memory_obj,
            }
        )

        try:
            result = cur_conversation({"query": user_prompt})
            response = format_response(result['result'])
            print("response: ", response)

            if response["answer"] == "NONE":
                user_prompt = get_prompt_suggestion_doc(user_prompt, doc_id, history)
                print("user_prompt: ", user_prompt)
                result = cur_conversation({"query": user_prompt})
                response = format_response(result['result'])
                print("response: ", response)

                if response["answer"] == "NONE":
                    result = get_simple_response(user_prompt, cur_conv, user_id, history)
                    print("result: ", result)
                    if result["status"] == "success":
                        response["answer"] = result["message"]
                    else:
                        return {
                            "status": "error",
                            "message": "Error while getting response",
                            "conversation_id": str(cur_conv),
                            "data": {
                                "response": "Error while getting response",
                            }
                        }


        except Exception as e:
            save_error(e)
            return {
                "status": "error",
                "message": "Error while getting response",
                "conversation_id": str(cur_conv),
                "data": {
                    "response": str(e),
                }
            }

        history.append({
            "prompt": prompt,
            "answer": response["answer"]
        })

        follow_up = get_follow_up_questions_doc(doc_id, history)

        follow_up_str = "\n".join(follow_up)
        hist_id = add_history(cur_conv, prompt, response["answer"], follow_up_str)

        source = []
        if result["source_documents"] is not None:
            source = result["source_documents"]

        return {
            "status": "success",
            "message": "Agent response",
            "data": {
                "response": response["answer"],
                "follow_up_questions": follow_up,
                "source": DocumentsToStr(result["source_documents"]),
                "conversation_id": str(cur_conv),
                "history_id": hist_id
            }
        }

    else:
        save_error("No document selected")
        return {
            "status": "error",
            "message": "No document selected",
            "conversation_id": None
        }


def get_follow_up_questions_doc(doc_id, history):

    if doc_id is not None:
        doc = get_doc_by_id(doc_id)

        hist = ""
        if history is None:
            history = []
        history = history[-3:]
        for h in history:
            hist += "question: " + h["prompt"] + "\n"
            hist += "answer: " + h["answer"] + "\n"

        tmp = "Suggest 3 follow up questions based on the  document summary, document name " \
            "and history of the conversation." \
            "Give more attention to the last question and answer in the history." \
            "Answer only the follow up questions. Don't try to make up an answer. Separate them with new line" \
            "<document summary>" + doc['summary'] + "</document summary>" \
            "<document name>" + doc['name'] + "</document name>" \
            "<history>" + hist + "</history>," \
            "Follow up questions: "

        system = PromptTemplate(
            template="",
            input_variables=[],
        )
        system_message_prompt = SystemMessagePromptTemplate(prompt=system)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        chain = LLMChain(llm=llm, prompt=chat_prompt)

        try:
            response = chain.run(text=tmp)
            response = response.replace("Follow up questions: ", "")
            response = response.split("\n")
            return response

        except Exception as e:
            save_error(e)
            return []


def get_prompt_suggestion_doc(prompt, doc_id, history):
    # TODO: Rewrite the prompt with the API (give summary of the document and the name of the document)
    doc = get_doc_by_id(doc_id)
    title = doc["name"]
    summary = doc["summary"]

    hist = ""
    if history is None:
        history = []
    for h in history:
        hist += "question: " + h["prompt"] + "\n"
        hist += "answer: " + h["answer"] + "\n"

    tmp = "Give a revised and optimized prompt based on the original prompt, document summary, document " \
          "name and history of the conversation." \
          "The prompt should be related to the document and to original prompt." \
          "Answer only the optimized prompt. Don't try to make up an answer." \
          "<document summary>" + summary + "</document summary>" \
          "<document name>" + title + "</document name>" \
          "<history>" + hist + "</history>," \
          "<original prompt>" + prompt + "</original prompt>"\
          "Optimized prompt: "

    system = PromptTemplate(
        template="",
        input_variables=[],
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=system)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=llm, prompt=chat_prompt)

    try:
        response = chain.run(text=tmp)
        response = response.replace("Optimized prompt: ", "")
        return response

    except Exception as e:
        save_error(e)
        return prompt


# TESTING AND EXPERIMENTS
# def multichain():
#     """
#     Test multichain query
#     :return:
#     """
#     print("Multichain")
#
#     embeddings = OpenAIEmbeddings()
#     docsearch1 = Chroma(persist_directory="./db/866136357063950337", embedding_function=embeddings).as_retriever(
#         search_kwargs={"k": 3})
#     docsearch2 = Chroma(persist_directory="./db/866149744008953857", embedding_function=embeddings).as_retriever(
#         search_kwargs={"k": 3})
#
#     retriever_infos = [
#         {
#             "name": "Cancer Culture",
#             "description": "Good for answering questions about the Cancer culture book",
#             "retriever": docsearch1
#         },
#         {
#             "name": "History and condition for creativity",
#             "description": "Good for answer questions about Creativity",
#             "retriever": docsearch2
#         }
#     ]
#
#     chain = MultiRetrievalQAChain.from_retrievers(llm, retriever_infos, verbose=True)
#
#     prompt = "What is the book cancer culture about?"
#
#     _DEFAULT_TEMPLATE = """Given the context information answer the following question
#                                 If you don't know the answer, just say you dont know Don't try to make up an answer.
#                                 =========
#                                 Always answer in the format:
#                                 ANSWER: <your answer>
#                                 FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
#                                 SOURCE: <do not make up source, give the page or the chapter from the document>
#                                 =========
#                                 question: {}""".format(prompt)
#
#     response = chain.run(prompt)
#     print(response)


# def get_summary_response(prompt):
#     """
#     Get response over the multiple index test
#     :param prompt:
#     :return:
#     """
#     print("\n")
#     print(prompt)
#     index_dir = os.path.join(persist_directory, "summary")
#     embeddings = OpenAIEmbeddings()
#     docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)
#     cur_conversation = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff",
#                                                                    retriever=docsearch.as_retriever(
#                                                                        search_kwargs={"k": 3}))
#
#     _DEFAULT_TEMPLATE = """Given the context information answer the following question
#                                 If you don't know the answer, just say you dont know Don't try to make up an answer.
#                                 =========
#                                 Always answer in the format:
#                                 ANSWER: <your answer>
#                                 FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
#                                 SOURCE: <do not make up source, give the page or the chapter from the document>
#                                 =========
#                                 question: {}""".format(prompt)
#
#     result = cur_conversation({"question": _DEFAULT_TEMPLATE})
#     response = format_response(result["answer"])
#     print(response)
#     return response
