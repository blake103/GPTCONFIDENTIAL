import os
import openai
import dotenv
dotenv.load_dotenv()
openai.organization = "org-DYgKCF2xF9A9IkNRwlyJL2EZ"
openai.api_key = os.getenv("API_KEY")
openai.Model.list()

message = {"role":"user", "content": input("This is the beginning of your chat with AI. [To exit, send \"###\".]\n\nYou:")}

conversation = [{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo. Act as a sentiment analysis AI and return the sentiment of the statements to the user -- Be as specific about the sentiment as possible."}]

while(message["content"]!="###"):
    conversation.append(message)
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=conversation) 
    message["content"] = input(f"Assistant: {completion.choices[0].message.content} \nYou:")
    print()
    conversation.append(completion.choices[0].message)

"""
response = openai.Completion.create(
engine="gpt-3.5-turbo",
prompt="where do you live?",
temperature=0.7,
max_tokens=1000,
top_p=1,
frequency_penalty=0,
presence_penalty=0,
messages=messages
)

# Get the completed text
completed_text = response.choices[0].text

# Replace any double line breaks with single line breaks
completed_text = completed_text.replace("\n\n", "\n")

# Use the completed text in your code
print("The completed text is: \n", completed_text)
"""
