# Imports and API setup
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import panel as pn  # GUI
load_dotenv()
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)




# Define helper functions for chat(one shot)
def get_completion(prompt, model=model):
    messages = [UserMessage(content=prompt)]
    return get_completion_from_messages(messages, model=model)

# function that actually talks with user and store all the history
def get_completion_from_messages(messages, model=model, temperature=0):
    response = client.complete(
        messages=messages,
        temperature=temperature,
        top_p=1,
        model=model
    )
    return response.choices[0].message.content
# Initialize Panel GUI
pn.extension()

# Track chat history and display
panels = []  # stores GUI elements
dashboard_context = [
    {'role': 'system', 'content': """
    You are OrderBot, an automated service to collect orders for a pizza restaurant. 
    You first greet the customer, then collect the order, and then ask if it's a pickup or delivery. 
    You wait to collect the entire order, then summarize it and check for a final time if the customer wants to add anything else. 
    If it's a delivery, you ask for an address. 
    Finally you collect the payment.
    Make sure to clarify all options, extras and sizes to uniquely identify the item from the menu.
    You respond in a short, very conversational friendly style.
    The menu includes:
    - pepperoni pizza: $12.95 (large), $10.00 (medium), $7.00 (small)
    - cheese pizza: $10.95, $9.25, $6.50
    - eggplant pizza: $11.95, $9.75, $6.75
    - fries: $4.50, $3.50
    - greek salad: $7.25
    - Toppings: extra cheese $2.00, mushrooms $1.50, sausage $3.00, canadian bacon $3.50, AI sauce $1.50, peppers $1.00
    - Drinks: coke $3.00 (large), $2.00 (medium), $1.00 (small), sprite same prices, bottled water $5.00
    """}
]

# Function to process input and update chat
def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''  # clear input field
    dashboard_context.append({'role': 'user', 'content': prompt})
    response = get_completion_from_messages(dashboard_context)
    dashboard_context.append({'role': 'assistant', 'content': response})

    panels.append(pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(pn.Row('Assistant:', pn.pane.Markdown(f"<div style='background-color:#F6F6F6; padding:10px;'>{response}</div>", width=600, sizing_mode="stretch_width")))
    return pn.Column(*panels)

# Create input box and button
inp = pn.widgets.TextInput(value="Hi", placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Chat!")
interactive_conversation = pn.bind(collect_messages, button_conversation)

# Build GUI layout
dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

# Display the dashboard (for Panel server)
dashboard.servable()
