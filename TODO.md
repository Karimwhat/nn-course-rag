
[x] OCR transcribe the lectures
[ ] Chunk and embed lectures
[ ] RAG Q&A baseline




"...text..." => [vector of numbers] # vector 

"This cup of coffee is hot"  => Embedding Function/Model => [8, 4, 2, 1] 
"This cup of coffee is cold" => Embedding Function/Model => [8, 4, -2, 1]
                                 ^ all-MiniLM-L6-v2        
                                 ^ gemini-embedding-002

1 Chunk => Embedding Function/Model => Embedding/Vector

-----------------------------------------------------------------------------

RAG:
    INPUT: User Question

    UNDER THE HOOD:
        - Retrieval: Question => embedding Function/Model => embedding/vector
            ex: "What beverages do you have?" => Embedding Function/Model => [7, 4, 0, 1]

        - Similarity search for similar chunks by measuring the distance to their embedding.
        => Top-k results. 
        E.g. 5 most similar chunks to my question:
            1. "Chunk from Lec1"
            2. "Chunk from Lec2" 
            3. "Chunk from Lec1"
            ...
        
        - We feed the chunks to the LLM context

    OUTPUT: result from the answer LLM

----Fallback project cutoff

[ ] Benchmark Question and Answers (json of question/answer pairs)
    [
        {
            "question": "What is gradient descent?",
            "answer": "...",
        },
        {
            "question": "What is gradient descent?",
            "answer": "...",
        },
    ]
[ ] Q&A Judge LLM
    [ ] Run RAG Q&A on benchmark questions
[ ] Improve RAG baseline by adjusting RAG hyper parameters
    [ ] All lectures in the context
    [ ] RAG chunks: varying chunk length
    [ ] RAG chunks: varying chunk overlap
