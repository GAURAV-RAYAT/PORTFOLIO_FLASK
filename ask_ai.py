import requests
import json

def ask_gaurav_ai(question):
    url = "https://gauravrayat.me/api/ask"
    
    # Define the payload
    payload = {
        "question": question
    }
    
    # Define headers
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Send the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('answer')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    user_query = input("Ask a question about Gaurav Rayat: ")
    ask_gaurav_ai(user_query)