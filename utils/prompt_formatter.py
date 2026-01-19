def format_context(chunks):
    """
    Formats retrieved chunks into a readable context block
    for the LLM prompt.
    """
    formatted_chunks = []

    for idx, chunk in enumerate(chunks, start=1):
        formatted_chunks.append(
            f"[{idx}] {chunk['text']}\n"
            f"(Source: {chunk['source']}, "
            f"Category: {chunk['category']})"
        )

    return "\n\n".join(formatted_chunks)
