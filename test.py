from conversation.conv import multichain, get_summary_response, get_simple_response
from conversation.ll_conv import load_multiple_indexes, create_index
from vectordb.vectordb import create_vector_index_folder

# multichain()
# create_vector_index_folder()


# response = get_summary_response("What is this book about?")
# if len(response['follow_up_questions']) > 2:
#     response = get_summary_response(response['follow_up_questions'][2])
# if len(response['follow_up_questions']) > 0:
#     response = get_summary_response(response['follow_up_questions'][1])
# response = get_summary_response("What is the cancer culture about?")
# response = get_summary_response("What is the main ideas about creativity there?")

response = get_simple_response("What is the Cancer culture idea?", None, 0, None)

print(response)