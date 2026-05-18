from openai import OpenAI
 
endpoint = "<open ai endpoint"
deployment_name = "gpt-4.1"
api_key = "<api key>"
 
client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

messages = [
            {
                "role": "system",
                "content":"you are a senior researcher",
            }
        ]
while True:
 
    text = input("enter my prompt:")
    if (text=="quit"):
        break
    messages.append(
            {
                "role": "user",
                "content": text,
            })
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
    )

 
    print(completion.choices[0].message.content)
    messages.append(
            {
                "role": "assistant",
                "content":completion.choices[0].message.content,
            })
    
print(messages)
 