from prompt import system_prompt
import ollama
import re
import subprocess

def run_steps(task):
    response = ""
    for s in ollama.chat(model='llama3', messages=task['messages'], stream=True):
        response += s['message']['content']
    task['messages'].append({"role": "assistant", "content": response})

    task['answer'] = re.search("Answer: (.*)$", response)
    if task.get('answer'):
        return

    output = 'Error: Please follow the "Statement: " format. Try again.'
    try:
        statement = re.search("Statement: (.+)", response).group(1)
        command = """./.venv/Scripts/python.exe -c "import numpy as np ; import pandas as pd ; df = pd.read_csv('./his_typhoon_20241016.csv', encoding='UTF-8') ; output = {} ; print(output)" """.format(statement)
        process = subprocess.run(command, capture_output=True, text=True)
        output = process.stdout if process.stdout else process.stderr

        if statement in output:
            output = "Error: Please use the valid Python syntax. Try again."
    except:
        pass
    
    task['messages'].append({"role": "user", "content": f"Output: {output}"})

    print(f"{response}\nOutput: {output}")

    return

if __name__ == "__main__":
    # task_input = "What are the columns' average?"
    task_input = input("Enter your question: ")
    
    task = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_input}
        ],
        "answer": None,
    }

    turns = 0
    max_turns = 20
    while turns < max_turns and not task.get("answer"):
        turns += 1
        run_steps(task)

    if turns == max_turns:
        print("Max turn exceeded")
        exit()
        
    answer = task.get("answer").group(1)
    print(answer)