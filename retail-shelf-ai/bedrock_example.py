"""
AWS Bedrock LLM Integration Example

This script demonstrates how to call AWS Bedrock LLM models.
No traditional API keys required - uses AWS IAM credentials instead.

Prerequisites:
1. AWS IAM credentials (ACCESS_KEY_ID, SECRET_ACCESS_KEY)
2. IAM permissions: bedrock:InvokeModel
3. Model access granted in AWS Bedrock console
4. Install: pip install boto3
"""

import boto3
import json
import os
from typing import Dict, List, Optional


class BedrockClient:
    """Client for interacting with AWS Bedrock LLM models."""
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        aws_access_key_id = "ASIA5GQV7PL66PXOPJIS",
        aws_secret_access_key = "u1+2WieapFAxFdv4FA7xU6c0m2N+G3NFAq2FdFmc",
        aws_session_token = "IQoJb3JpZ2luX2VjEOD//////////wEaCXVzLWVhc3QtMSJGMEQCIAa253U6PEoce6fFkY/vi3CiAl4Vwy+xuM169YsHZCq+AiAF/O8zGK7hA5A2RTajHxGpus+AvH4sHCw9654VUhKEESqhAgip//////////8BEAEaDDkwNzM1Nzk0NDU3MyIMUNA8ARSEPWyULdL0KvUBoxGrv8MgYDsDxZH0RF2JEcLx6RQAfCiKXKKz8J5EABFZ+DSsPMObcsn1YjB4smHiJv2MGhRAllYVwJ6go9krNGmw649bVGyrhH1fxl7IYKjhAyquo8BP7aWzRr8HVdrfs8uCpXMNlKgYu0hkGWqFVVAKwaEkOEv6cAQkqOho6P0wp6wsLKXsLJjiWvC/YmqrKi1YU9106/Y4X/IEdZ0laNeZSgp5jGf9JyRg016/we4MCYmG2QNUKZCXyLugBU6gJH11tOLo1X9QIGbIpIobGATkZ1ve/d91T6W9y4vMFUHSscGYFS1xFoDGrlmnHeyhU10+poQwiryEywY6ngGUZtsVqZjT8PNQJCwBLXm6nsZOfUjWSd2xyxW+FIh2gvCHdFjOicNqy7/f+wCIofxZ9oTVZM+mnAO4ERyXa+1KzdgICtSReXLdwGt4e6PtfyUdVMBcHRQxyNNBoN/RraimRiXqBmmX9E/b2XfUO4enPujAYTuqaOxuRMvVAS4r9OVT2Tc2XP4r4PsFYGFsU2mE5q52soexfffGU0rwzA=="
    ):
        """
        Initialize Bedrock client.
        
        Args:
            region_name: AWS region where Bedrock is available
            aws_access_key_id: AWS access key (or set AWS_ACCESS_KEY_ID env var)
            aws_secret_access_key: AWS secret key (or set AWS_SECRET_ACCESS_KEY env var)
            aws_session_token: Optional session token for temporary credentials
        """
        self.region_name = region_name
        
        # Initialize boto3 client for Bedrock Runtime
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': region_name
        }
        
        # Add credentials if provided (otherwise boto3 will use environment/config)
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs['aws_access_key_id'] = aws_access_key_id
            client_kwargs['aws_secret_access_key'] = aws_secret_access_key
            if aws_session_token:
                client_kwargs['aws_session_token'] = aws_session_token
        
        self.client = boto3.client(**client_kwargs)
    
    def invoke_claude(
        self,
        messages: List[Dict[str, str]],
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        max_tokens: int = 1024,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> str:
        """
        Invoke Claude model on AWS Bedrock.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model_id: Claude model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system: Optional system prompt
            
        Returns:
            Generated text response
        """
        # Prepare request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }
        
        if system:
            body["system"] = system
        
        try:
            # Invoke the model
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            print(f"Error invoking Bedrock model: {e}")
            raise
    
    def invoke_titan(
        self,
        prompt: str,
        model_id: str = "amazon.titan-text-express-v1",
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke Amazon Titan model on AWS Bedrock.
        
        Args:
            prompt: Input text prompt
            model_id: Titan model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 0.9
            }
        }
        
        try:
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['results'][0]['outputText']
            
        except Exception as e:
            print(f"Error invoking Bedrock model: {e}")
            raise
    
    def list_available_models(self):
        """List available foundation models in Bedrock."""
        try:
            # Use bedrock client (not bedrock-runtime) for listing
            bedrock = boto3.client('bedrock', region_name=self.region_name)
            response = bedrock.list_foundation_models()
            
            print("\n📋 Available Bedrock Models:")
            for model in response['modelSummaries']:
                print(f"   - {model['modelId']}")
                print(f"     Provider: {model['providerName']}")
                print(f"     Input: {model.get('inputModalities', [])}")
                print(f"     Output: {model.get('outputModalities', [])}")
                print()
                
        except Exception as e:
            print(f"Error listing models: {e}")
            print("Note: Requires bedrock:ListFoundationModels permission")


def main():
    """Example usage of AWS Bedrock integration."""
    
    # Option 1: Use environment variables (recommended)
    # export AWS_ACCESS_KEY_ID=your_access_key
    # export AWS_SECRET_ACCESS_KEY=your_secret_key
    # export AWS_DEFAULT_REGION=us-east-1
    
    # Option 2: Pass credentials explicitly (not recommended for production)
    client = BedrockClient(
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        # aws_access_key_id="YOUR_ACCESS_KEY",
        # aws_secret_access_key="YOUR_SECRET_KEY"
    )
    
    # Example 1: Call Claude for text generation
    print("🤖 Example 1: Claude 3.5 Sonnet")
    print("-" * 50)
    
    messages = [
        {
            "role": "user",
            "content": "Explain what AWS Bedrock is in 2 sentences."
        }
    ]
    
    try:
        response = client.invoke_claude(
            messages=messages,
            max_tokens=200,
            temperature=0.7,
            system="You are a helpful AI assistant."
        )
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have:")
        print("  1. Valid AWS credentials configured")
        print("  2. bedrock:InvokeModel permission")
        print("  3. Model access granted in Bedrock console")
        print("  4. Bedrock available in your region\n")
    
    # Example 2: Call Claude for analysis (relevant to retail shelf AI)
    print("🤖 Example 2: Product Analysis")
    print("-" * 50)
    
    messages = [
        {
            "role": "user",
            "content": "List 5 key metrics for evaluating a retail shelf product detection system."
        }
    ]
    
    try:
        response = client.invoke_claude(
            messages=messages,
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            max_tokens=500
        )
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 3: List available models (optional)
    print("🤖 Example 3: List Available Models")
    print("-" * 50)
    # Uncomment to list all available models:
    # client.list_available_models()


if __name__ == "__main__":
    print("=" * 60)
    print("AWS Bedrock LLM Integration Example")
    print("=" * 60)
    print()
    print("Required Information:")
    print("  ✓ AWS_ACCESS_KEY_ID (IAM credential)")
    print("  ✓ AWS_SECRET_ACCESS_KEY (IAM credential)")
    print("  ✓ AWS_DEFAULT_REGION (e.g., us-east-1)")
    print("  ✓ IAM Permission: bedrock:InvokeModel")
    print("  ✓ Model access granted in Bedrock console")
    print()
    print("Available Models (examples):")
    print("  • anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("  • anthropic.claude-3-haiku-20240307-v1:0")
    print("  • amazon.titan-text-express-v1")
    print("  • meta.llama3-70b-instruct-v1:0")
    print()
    print("=" * 60)
    print()
    
    main()
