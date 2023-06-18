# from conversation.conv import multichain, get_summary_response, get_simple_response
# from conversation.ll_conv import load_multiple_indexes, create_index
# from vectordb.vectordb import create_vector_index_folder
#
# # multichain()
# # create_vector_index_folder()
#
#
# # response = get_summary_response("What is this book about?")
# # if len(response['follow_up_questions']) > 2:
# #     response = get_summary_response(response['follow_up_questions'][2])
# # if len(response['follow_up_questions']) > 0:
# #     response = get_summary_response(response['follow_up_questions'][1])
# # response = get_summary_response("What is the cancer culture about?")
# # response = get_summary_response("What is the main ideas about creativity there?")
#
# response = get_simple_response("What is the Cancer culture idea?", None, 0, None)
#
# print(response)

# text = "FOLLOW UP: The document emphasizes the importance of clear Communication and defines words that may have multiple meanings. The author."
#
# print(text.capitalize())
# print(text.title())
# print(text.upper())
# print(text.lower())
# print(text.swapcase())
# print(text.casefold())

# a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# print(a[-4:])

import openai
from dotenv import load_dotenv

load_dotenv()

response = openai.Moderation.create(
    input="""
 How does Graham Harman define "weird realism" in his book?
""", api_key="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"
)
moderation_output = response["results"][0]
print(moderation_output.flagged == False)
