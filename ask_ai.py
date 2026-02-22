import requests
import json

def ask_gaurav_ai(question):
    url = "https://gauravrayat.me/api/ask"
    
    payload = {
        "question": question
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result.get('answer')}\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("--- Gaurav Rayat AI Assistant (Terminal Mode) ---")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_query = input("👤 You: ")
        
        # Check if the user wants to exit
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if user_query.strip():
            ask_gaurav_ai(user_query)