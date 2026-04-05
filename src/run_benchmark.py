import json
import argparse
import sys
import time
from typing import List, Dict

from query_vector_store import query_vector_store, initialize_vector_store_llm

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def grade_answer(judge_llm, question: str, ground_truth: str, student_answer: str) -> int:
    """
    Uses the Judge LLM to compare the student answer against the ground truth.
    Returns an integer score (0, 1, or 2).
    """
    
    system_prompt = """
    You are an expert grader. You will be provided with a Question, a Ground Truth Answer, and a Student Answer.
    Your task is to grade the Student Answer based on its accuracy compared to the Ground Truth.
    
    Assign a score based on these criteria:
    2: Fully correct. The answer matches the ground truth logic and values.
    1: Partially correct. The student has the right idea but made a calculation error or missed a step.
    0: Incorrect. The answer is wrong or irrelevant.

    Return ONLY the integer (0, 1, or 2). Do not provide any explanation.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """
            Question: {question}
            
            Ground Truth: {ground_truth}
            
            Student Answer: {student_answer}
        """)
    ])

    chain = prompt | judge_llm | StrOutputParser()

    try:
        response = chain.invoke({
            "question": question,
            "ground_truth": ground_truth,
            "student_answer": student_answer
        })
        # Extract the first digit found in the response to be safe
        score = int(''.join(filter(str.isdigit, response.strip()))[0])
        return score
    except Exception as e:
        print(f"Error grading question: {e}")
        return 0

def main():
    # 1. Take in an input name for the benchmark
    parser = argparse.ArgumentParser(description="Run RAG Benchmark")
    parser.add_argument("--name", type=str, required=True, help="Benchmark name (e.g. 'noRAG')")
    parser.add_argument("--input", type=str, default="data/benchmark/benchmark.json", help="Path to benchmark JSON")
    parser.add_argument("--topK", type=int, default=10, help="TopK number (e.g., '7')")
    args = parser.parse_args()

    benchmark_name = args.name
    input_file = args.input
    topK_number = args.topK
    

    # 2. Initialize LLM and vector store
    # Note: We use the returned 'llm' as our Judge as well
    vector_store, llm = initialize_vector_store_llm()

    # Load benchmark questions
    with open(input_file, 'r') as f:
        questions_data = json.load(f)

    results = []
    total_points_earned = 0
    max_possible_points = len(questions_data) * 2  # Assuming 2 is the max score per question

    print(f"Starting benchmark: {benchmark_name}")

    # 3. Loop through benchmark
    for item in questions_data:
        q_num = item["question_number"]
        q_text = item["question_text"]
        ground_truth = item["answer"]

        print(f"Processing Question {q_num}...")

        # Get student answer from RAG system
        while True:
            try:
                student_answer = query_vector_store(
                    query=q_text, 
                    vector_store=vector_store, 
                    llm=llm, 
                    enable_rag=True, 
                    top_k=topK_number
                )
                break
            except Exception as e:
                # Check for "429" in the error message 
                if "429" in str(e):
                    print("Rate limit detected in error message. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    raise e
                

        # Using langchain to grade the answer
        while True:
            try:
                score = grade_answer(llm, q_text, ground_truth, student_answer)
                break
            except Exception as e:
                # Check for "429" in the error message 
                if "429" in str(e):
                    print("Rate limit detected in error message. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    raise e
        
        
        results.append({
            "question_number": q_num,
            "answer": student_answer,
            "answer_score": score
        })
        
        total_points_earned += score

    # 4. Calculate final score
    final_percentage = (total_points_earned / max_possible_points) * 100 if max_possible_points > 0 else 0

    output_data = {
        "results": results,
        "total_score_out_of_100": round(final_percentage, 2)
    }

    # 5. Store the result
    output_filename = f"results/benchmark_result_{benchmark_name}.json"
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

    print(f"Benchmark complete. Results saved to {output_filename}")
    print(f"Final Score: {final_percentage}%")

if __name__ == "__main__":
    main()