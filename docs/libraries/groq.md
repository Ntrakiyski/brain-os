roq Python API library
PyPI version

The Groq Python library provides convenient access to the Groq REST API from any Python 3.9+ application. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients powered by httpx.

It is generated with Stainless.

Documentation
The REST API documentation can be found on console.groq.com. The full API of this library can be found in api.md.

Installation
# install from PyPI
pip install groq
Usage
The full API of this library can be found in api.md.

import os
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        }
    ],
    model="openai/gpt-oss-20b",
)
print(chat_completion.choices[0].message.content)
While you can provide an api_key keyword argument, we recommend using python-dotenv to add GROQ_API_KEY="My API Key" to your .env file so that your API Key is not stored in source control.

Async usage
Simply import AsyncGroq instead of Groq and use await with each API call:

import os
import asyncio
from groq import AsyncGroq

client = AsyncGroq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            }
        ],
        model="openai/gpt-oss-20b",
    )
    print(chat_completion.choices[0].message.content)


asyncio.run(main())
Functionality between the synchronous and asynchronous clients is otherwise identical.

With aiohttp
By default, the async client uses httpx for HTTP requests. However, for improved concurrency performance you may also use aiohttp as the HTTP backend.

You can enable this by installing aiohttp:

# install from PyPI
pip install groq[aiohttp]
Then you can enable it by instantiating the client with http_client=DefaultAioHttpClient():

import os
import asyncio
from groq import DefaultAioHttpClient
from groq import AsyncGroq


async def main() -> None:
    async with AsyncGroq(
        api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
        http_client=DefaultAioHttpClient(),
    ) as client:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Explain the importance of low latency LLMs",
                }
            ],
            model="openai/gpt-oss-20b",
        )
        print(chat_completion.id)


asyncio.run(main())
Using types
Nested request parameters are TypedDicts. Responses are Pydantic models which also provide helper methods for things like:

Serializing back into JSON, model.to_json()
Converting to a dictionary, model.to_dict()
Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set python.analysis.typeCheckingMode to basic.

Nested params
Nested parameters are dictionaries, typed using TypedDict, for example:

from groq import Groq

client = Groq()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "content": "string",
            "role": "system",
        }
    ],
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    compound_custom={},
)
print(chat_completion.compound_custom)
File uploads
Request parameters that correspond to file uploads can be passed as bytes, or a PathLike instance or a tuple of (filename, contents, media type).

from pathlib import Path
from groq import Groq

client = Groq()

client.audio.transcriptions.create(
    model="whisper-large-v3-turbo",
    file=Path("/path/to/file"),
)
The async client uses the exact same interface. If you pass a PathLike instance, the file contents will be read asynchronously automatically.

Handling errors
When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of groq.APIConnectionError is raised.

When the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of groq.APIStatusError is raised, containing status_code and response properties.

All errors inherit from groq.APIError.

import groq
from groq import Groq

client = Groq()

try:
    client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "Explain the importance of low latency LLMs",
            },
        ],
        model="openai/gpt-oss-20b",
    )
except groq.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except groq.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except groq.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
Error codes are as follows:

Status Code	Error Type
400	BadRequestError
401	AuthenticationError
403	PermissionDeniedError
404	NotFoundError
422	UnprocessableEntityError
429	RateLimitError
>=500	InternalServerError
N/A	APIConnectionError
Retries
Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the max_retries option to configure or disable retry settings:

from groq import Groq

# Configure the default for all requests:
client = Groq(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        },
    ],
    model="openai/gpt-oss-20b",
)
Timeouts
By default requests time out after 1 minute. You can configure this with a timeout option, which accepts a float or an httpx.Timeout object:

from groq import Groq

# Configure the default for all requests:
client = Groq(
    # 20 seconds (default is 1 minute)
    timeout=20.0,
)

# More granular control:
client = Groq(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        },
    ],
    model="openai/gpt-oss-20b",
)
On timeout, an APITimeoutError is thrown.

Note that requests that time out are retried twice by default.

Advanced
Logging
We use the standard library logging module.

You can enable logging by setting the environment variable GROQ_LOG to info.

$ export GROQ_LOG=info
Or to debug for more verbose logging.

How to tell whether None means null or missing
In an API response, a field may be explicitly null, or missing entirely; in either case, its value is None in this library. You can differentiate the two cases with .model_fields_set:

if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
Accessing raw response data (e.g. headers)
The "raw" Response object can be accessed by prefixing .with_raw_response. to any HTTP method call, e.g.,

from groq import Groq

client = Groq()
response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "system",
        "content": "You are a helpful assistant.",
    }, {
        "role": "user",
        "content": "Explain the importance of low latency LLMs",
    }],
    model="openai/gpt-oss-20b",
)
print(response.headers.get('X-My-Header'))

completion = response.parse()  # get the object that `chat.completions.create()` would have returned
print(completion.id)
These methods return an APIResponse object.

The async client returns an AsyncAPIResponse with the same structure, the only difference being awaitable methods for reading the response content.

.with_streaming_response
The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use .with_streaming_response instead, which requires a context manager and only reads the response body once you call .read(), .text(), .json(), .iter_bytes(), .iter_text(), .iter_lines() or .parse(). In the async client, these are async methods.

with client.chat.completions.with_streaming_response.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        },
    ],
    model="openai/gpt-oss-20b",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
The context manager is required so that the response will reliably be closed.

Making custom/undocumented requests
This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

Undocumented endpoints
To make requests to undocumented endpoints, you can make requests using client.get, client.post, and other http verbs. Options on the client will be respected (such as retries) when making this request.

import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
Undocumented request params
If you want to explicitly send an extra param, you can do so with the extra_query, extra_body, and extra_headers request options.

Undocumented response properties
To access undocumented response properties, you can access the extra fields like response.unknown_prop. You can also get all the extra fields on the Pydantic model as a dict with response.model_extra.

Configuring the HTTP client
You can directly override the httpx client to customize it for your use case, including:

Support for proxies
Custom transports
Additional advanced functionality
import httpx
from groq import Groq, DefaultHttpxClient

client = Groq(
    # Or use the `GROQ_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
You can also customize the client on a per-request basis by using with_options():

client.with_options(http_client=DefaultHttpxClient(...))
Managing HTTP resources
By default the library closes underlying HTTP connections whenever the client is garbage collected. You can manually close the client using the .close() method if desired, or with a context manager that closes when exiting.

from groq import Groq

with Groq() as client:
  # make requests here
  ...

# HTTP client is now closed
Versioning
This package generally follows SemVer conventions, though certain backwards-incompatible changes may be released as minor versions:

Changes that only affect static types, without breaking runtime behavior.
Changes to library internals which are technically public but not intended or documented for external use. (Please open a GitHub issue to let us know if you are relying on such internals.)
Changes that we do not expect to impact the vast majority of users in practice.
We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an issue with questions, bugs, or suggestions.

Determining the installed version
If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

import groq
print(groq.__version__)