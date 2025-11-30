from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI

try:
    
    # Connect using Azure CLI credential
    project_endpoint = "https://ducnguyenhuu123-resource.services.ai.azure.com/api/projects/ducnguyenhuu123"


    credential = AzureCliCredential()
    project_client = AIProjectClient(
    credential=credential,
    endpoint=project_endpoint)

        # Get a chat client
    chat_client = project_client.get_openai_client(api_version="2024-10-21")
    print(chat_client.models.list())

    '''
    # Get a chat completion - try with correct deployment name
    user_prompt = input("\nWhat should I do in thanksgiving break: ")
    
    # Change this to your actual deployment name from the list above
    response = chat_client.chat.completions.create(
        model="gpt-4o-duc",  # ← Change this to actual deployment name
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": user_prompt}
        ]
    )
    print(response.choices[0].message.content)

    '''

except Exception as ex:
    print(ex)
    