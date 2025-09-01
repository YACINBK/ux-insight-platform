from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"

@app.route('/ask', methods=['POST'])
def ask_llm():
    data = request.json
    user_prompt = data.get('prompt', '')
    user_json = data.get('user_json', '')

    if not user_prompt or not user_json:
        return jsonify({'error': 'Both prompt and user_json are required'}), 400

    # Optionally, validate user_json is valid JSON
    try:
        parsed_json = json.loads(user_json)
    except Exception as e:
        return jsonify({'error': f'user_json is not valid JSON: {e}'}), 400

    # Construct the prompt for the LLM
    full_prompt = (
        f"{user_prompt}\n\n"
        f"Here is the user tracking data in JSON format:\n{user_json}\n\n"
        "Please analyze this data and provide insights and suggestions."
    )

    payload = {
        "model": "deepseek-coder:6.7b",
        "messages": [
            {"role": "user", "content": full_prompt}
        ]
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
        answer = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'message' in data and 'content' in data['message']:
                        answer += data['message']['content']
                except Exception:
                    continue
        return jsonify({'response': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)