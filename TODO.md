
[x] OCR transcribe the lectures
[x] Chunk and embed lectures
[x] RAG Q&A
[x] Benchmark Question and Answers (json of question/answer pairs)
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
[x] Q&A Judge LLM INPUT:
    [x] INPUT: question, ground truth answer, student answer, 
    [x] Q&A baseline using full context (no RAG)
    [x] Run RAG Q&A on benchmark questions
    [ ] Test performance 
        [ ] Provide all right answers or all wrong answers or use completely diff benchmark that has wrong questions etc, and check score.
        [ ] Look up QnA benchmarks gemini performance
        [ ] Judge LLM benchmark (look up)
[ ] Benchmarks:
    [ ] noRAG - pass entire lecture set
    [ ] RAG topk5
    [ ] RAG topk10
    [ ] RAG topk20
    [ ] Literally nothing (No RAG, and No context)
[ ] Presentation:
    [ ] Know the order of discussion points for presentation
        [ ] Main goal: Evaluate LLM Based student QnA based on lecture material
        [ ] Read Handwritten slides -> OCR into text -> OCR progress and methodology explained -> Benchmark -> RAG process and methodology explained -> Judge LLM -> ... rest of progress -> conclusion/results
    [ ] Understand why and what each relevant file does, and the main functions/calls within
[ ] Improve RAG baseline by adjusting RAG hyper parameters
    [ ] All lectures in the context
    [ ] Hyperparameters:
        [ ] Top-k
        [ ] Restrict context to fetched chunks vs. rely on LLM knowledge as well
        [ ] Chunk length
        [ ] Chunk overlap




"...text..." => [vector of numbers] # vector 

"This cup of coffee is hot"  => Embedding Function/Model => [8, 4, 2, 1] 
"This cup of coffee is cold" => Embedding Function/Model => [8, 4, -2, 1]
                                 ^ all-MiniLM-L6-v2        
                                 ^ gemini-embedding-002

1 Chunk => Embedding Function/Model => Embedding/Vector


-----------------------------------------------------------------------------
Vector store: file or database that stores the chunk <-> vector pair
This is what we would like if we exported it to json:
    [
        {
            "text": "This cup of coffee is hot",
            "embedding": [8,4,2,1]
        },
        {
            "text": "This cup of coffee is cold",
            "embedding": [8,4,-2,1]
        },
    ]

The reason we need a database or "store" is for performance: querying the similarity.
 
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


