# Ollama Cloud Model Tester

A Python command-line utility that discovers models exposed by Ollama Cloud and sends each model a small test prompt to check whether it can generate a response.

The tool prints a live streaming response for each model and classifies the result as **WORKING**, **RESTRICTED**, or **FAILED**. It also reports response latency and, when the API returns the required statistics, generation speed in tokens per second.

## Features

- **Dynamic model discovery:** Retrieves the available model list from `https://ollama.com/api/tags` instead of relying on a hardcoded model list.
- **Streaming tests:** Sends a test prompt to each discovered model and displays the response as it arrives.
- **Response validation:** Treats the exact response `WORKING` (ignoring surrounding whitespace and common punctuation, and case-insensitively) as a successful test.
- **Access restriction detection:** Identifies common subscription, authentication, billing, and quota-related errors.
- **Retry handling:** Retries selected temporary connection and server errors once.
- **Performance information:** Measures elapsed response time and displays token-generation speed when the API supplies the relevant statistics.
- **API-key handling:** Accepts an API key at runtime, checks the `OLLAMA_API_KEY` environment variable, and can reuse a key saved locally in `.ollama_api_key`.
- **Terminal interface:** Displays an animated banner, progress indicator, per-model results, and a final summary.

## Requirements

- Python 3.8 or newer (a recent Python 3 release is recommended).
- An Ollama Cloud API key with access to the models you want to test.
- An active internet connection.

Python packages are listed in [`requirements.txt`](requirements.txt):

- `requests`
- `ollama`

> A locally installed Ollama server is not required by this script. It connects to the Ollama Cloud host (`https://ollama.com`).

## Installation

Clone the repository:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

Create and activate a virtual environment (recommended).

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Usage

Run the script from the repository directory. For example, if the Python file is named `ollama_cloud_model_tester.py`:

```bash
python ollama_cloud_model_tester.py
```

The program will:

1. Display the tool banner.
2. Look for an API key in the `OLLAMA_API_KEY` environment variable.
3. If no environment-variable key is set, offer to reuse `.ollama_api_key` when that file exists; otherwise, prompt for an API key.
4. Ask whether to save the key in the tool directory for future runs.
5. Retrieve the model list from Ollama Cloud.
6. Test each discovered model and print the final results summary.

### API-key options

**Option 1 — Enter the key when prompted**

Run the script and enter the key when requested. The input uses a hidden prompt so the key is not echoed in the terminal.

**Option 2 — Use an environment variable**

PowerShell:

```powershell
$env:OLLAMA_API_KEY = "your_api_key_here"
python ollama_cloud_model_tester.py
```

Linux / macOS:

```bash
export OLLAMA_API_KEY="your_api_key_here"
python ollama_cloud_model_tester.py
```

**Option 3 — Save the key locally**

When prompted, choose `y` to save the key in `.ollama_api_key` beside the script. On Unix-like systems, the script attempts to set restrictive file permissions (`600`). The key file is stored in plain text, so protect your local machine and do not share the file.

## Understanding the results

| Status | Meaning |
|---|---|
| `WORKING` | The model returned the expected `WORKING` response. |
| `RESTRICTED` | The script detected an access, subscription, billing, or quota restriction. |
| `FAILED` | The request failed, or the model returned a response that did not match the expected test response. |

The final report includes the number of models tested in each category. For successful models, it also calculates average response latency and average generation speed when speed statistics are available.

**Note:** These labels are based on the script's response checks and keyword/status-code matching. They are a practical connectivity and response test, not a guarantee of model quality, general availability, or suitability for a particular workload. A `FAILED` result can also reflect a temporary service or network issue.

## Configuration

The main settings are defined near the top of the Python script:

| Setting | Current value | Purpose |
|---|---:|---|
| `TOOL_NAME` | `OLLAMA CLOUD MODEL TESTER` | Tool name constant. |
| `VERSION` | `3.0` | Version displayed in the banner. |
| `MAX_RETRIES` | `1` | Number of retries after the initial attempt for selected temporary errors. |
| `REQUEST_TIMEOUT` | `60` | Timeout passed to the Ollama Python client, in seconds. |
| Model-list timeout | `15` seconds | Timeout used when requesting the model list. |
| Retry delay | `2` seconds | Delay before a retry. |
| `EXPECTED_RESPONSE` | `WORKING` | Expected test response. |

The test prompt and restriction/retry keyword lists can also be adjusted in the configuration section of the script.

## Project structure

A simple repository layout:

```text
ollama-cloud-model-tester/
├── ollama_cloud_model_tester.py
├── README.md
├── requirements.txt
└── .gitignore
```

The `.ollama_api_key` file is created locally only if you choose to save your API key; it should not be committed to Git.

## Security

- **Never commit your API key.** The repository `.gitignore` should include `.ollama_api_key` and `.env`.
- Do not paste API keys into source code or public issues.
- If a key is accidentally published, revoke or rotate it through the relevant Ollama account controls.
- Environment variables are preferable to storing a key in a local plaintext file, especially on shared systems.

## Limitations

- Models are tested sequentially, not concurrently.
- Each model receives the same fixed test prompt.
- The tool does not benchmark long-form generation, reasoning quality, throughput under load, or model accuracy.
- The tool prints results to the terminal; it does not create a report file.
- Model availability and access depend on the Ollama Cloud account and service at test time.

## Disclaimer

This project is an independent utility for testing model access and basic response generation through Ollama Cloud. Use it with an API key you are authorized to use and in accordance with the provider's terms and rate limits. It is not an official Ollama product unless explicitly stated by the repository owner.

## License

Add a license file to the repository before distributing or reusing this project. Choose a license that matches how you want others to use the code.
