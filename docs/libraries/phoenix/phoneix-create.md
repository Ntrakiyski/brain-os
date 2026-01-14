Create a New Project

Python
TypeScript
Manual
Projects are created when you log your first trace via OpenTelemetry. See the documentation
 for a complete guide.
Install Dependencies
Use the Phoenix OTEL or OpenTelemetry
 to configure your application to send traces to Phoenix.

pip install arize-phoenix-otel
Setup your Environment
arize-phoenix-otel automatically picks up your configuration from environment variables

PHOENIX_API_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJBcGlLZXk6MSJ9.4ZPReqd5kGLEl5UTUTTD4K-Kyg8wNAKtLVeG5zfIc-4'
PHOENIX_COLLECTOR_ENDPOINT='https://app.phoenix.arize.com/s/ntrakiyski'
System API keys can be created and managed in Settings
Setup OpenTelemetry
Register your application to send traces to this project. The code below should be added BEFORE any code execution.

from phoenix.otel import register

tracer_provider = register(
  project_name="your-next-llm-project",
  endpoint="https://app.phoenix.arize.com/s/ntrakiyski",
  auto_instrument=True
)
To configure gRPC and batching, see our setup guide
.
Setup Instrumentation
Add instrumentation to your application so that your application code is traces.
Instrumentation
OpenAI Example
Install OpenInference
 instrumentation as well as openai


pip install openinference-instrumentation-openai openai
Instrument openai at the beginning of your code


from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
Use openai as you normally and traces will be sent to Phoenix


⌄
⌄
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",
)