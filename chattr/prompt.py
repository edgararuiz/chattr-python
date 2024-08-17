from requests import post
from json import dumps, loads
from sys import stdout

def chat(prompt, stream = True, history = [], preview = False):
    return(
        _ch_submit_ollama(
            prompt = prompt, 
            stream = stream,
            history = history,
            preview = preview
            )
        )

def _ch_submit_ollama(prompt, stream = True, history = [], preview = False):
    url = "http://localhost:11434/api/chat"

    headers = {
        "Content-Type": "application/json"
    }

    messages = []
    messages.append(dict(
        role =  "system", 
        content = "You are a helpful coding assistant that uses Python for data analysis. Keep comments to a minimum."
        ))
    messages.append(dict(
        role =  "user", 
        content = prompt
        ))

    data = {
        'model': 'llama2',
        'messages' :  messages, 
        'stream': stream
        }

    if preview:    
        print(data)
        return()

    response = post(url, data = dumps(data), headers = headers, stream = stream)
    for line in response.iter_lines():
        body = loads(line)
        resp = body.get("message")
        content = resp.get("content")
        stdout.write(content)

