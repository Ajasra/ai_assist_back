import json


def DocumentsToStr(documents):
    """
    Convert a list of documents to a string
    :param documents:
    :return:
    """
    sources = []
    for i in range(len(documents)):

        source = documents[i].page_content
        # clean the source from specisl characters to allow it write in SQL database
        source = source.replace("'", "''")
        source = source.replace('"', '""')

        title = documents[i].metadata["source"].split("/")[-1]
        # if "page" in documents[i]["metadata"]:
        #     title = title + ": " + documents[i]["metadata"]["page"]

        sources.append({
            "source": source,
            "title": title
        })

    # serialize the sources
    sources = json.dumps(sources)

    return sources