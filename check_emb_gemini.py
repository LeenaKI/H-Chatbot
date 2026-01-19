from google import genai

client = genai.Client(api_key="AIzaSyDq8eO24UmC-Nagdyuql05qAp5CCG4HbAo")

result = client.models.embed_content(
        model="gemini-embedding-001",
        contents="What is the meaning of life?")

print(result.embeddings)


"""
expected output:
python check_emb_gemini.py
[ContentEmbedding(
  values=[
    -0.022374554,
    -0.004560777,
    0.013309286,
    -0.0545072,
    -0.02090443,
    <... 3067 more items ...>,
  ]
)]


##generate embeddings for multiple chunks at once by passing them in as a list of strings.
from google import genai

client = genai.Client(api_key="AIzaSyDq8eO24UmC-Nagdyuql05qAp5CCG4HbAo")

result = client.models.embed_content(
        model="gemini-embedding-001",
        contents= [
            "What is the meaning of life?",
            "What is the purpose of existence?",
            "How do I bake a cake?"
        ])

for embedding in result.embeddings:
    print(embedding)
    """