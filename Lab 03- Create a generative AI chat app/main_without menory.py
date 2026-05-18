from openai import OpenAI
 
endpoint = "<open ai endpoint"
deployment_name = "gpt-4.1"
api_key = "<api key>"
 
client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)
while True:
 
    text = input("enter my prompt:")
    if (text=="quit"):
        break
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
    )
 
    print(completion.choices[0].message.content)
 