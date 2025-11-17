# Project Explanation: Code Assist MCP for Gemini CLI

## 1. Project Overview

This project is a **Code Assistant a Master Control Program (MCP)** designed to be used with the Gemini CLI. It acts as a backend server that exposes a set of powerful code-related tools to the Gemini CLI. These tools can be used to analyze, fix, review, test, and explain Python code.

The project is built with a modular architecture, making it easy to extend and add new tools. It leverages the Ollama agent to understand natural language queries and execute the appropriate tools to accomplish a given task.

## 2. Architecture

The project follows a modular and layered architecture:

- **MCP Server (`server.py`)**: This is the main entry point of the application. It uses the `FastMCP` library to create a server that exposes the tools to the Gemini CLI. It's responsible for defining the tools and handling incoming requests.

- **MCP Tools (`mcp_tools/`)**: This directory contains the tools that are directly exposed to the Gemini CLI through the MCP server. Each file in this directory defines one or more tools.

- **Agents (`agents/`)**: This directory contains the logic for the AI agents. The `OllamaAgent` is the core of this layer, responsible for interacting with the Ollama model. It uses a ReAct (Reasoning and Acting) pattern to understand user prompts and decide which tools to use.

- **Tools (`tools/`)**: This directory contains the underlying implementation of the code-related tools. These tools are not directly exposed to the Gemini CLI, but are used by the `OllamaAgent` to perform tasks like code analysis, execution, and documentation search.

- **Utils (`utils/`)**: This directory contains utility modules for configuration, logging, and caching.

## 3. Directory and File Structure

Here's a breakdown of the most important files and directories:

- **`server.py`**: The main entry point of the application. It initializes the `FastMCP` server and registers the tools from the `mcp_tools` directory.

- **`docker-compose.yml` & `Dockerfile`**: These files are used to containerize the application with Docker, making it easy to set up and run in a consistent environment.

- **`requirements.txt`**: This file lists all the Python dependencies required for the project.

- **`README.md`**: Provides a brief overview of the project, setup instructions, and usage examples.

- **`PROJECT_STRUCTURE.md`**: Describes the recommended project structure and lists the recommended libraries for different tasks.

- **`mcp_tools/`**:
    - `analyze_fix.py`: Defines the `analyze_and_fix` and `analyze_and_fix_advanced` tools for automatically fixing Python code.
    - `review.py`: Defines the `expert_review` and `expert_review_advanced` tools for performing code reviews.
    - `test_gen.py`: Defines the `generate_tests` tool for generating unit tests.
    - `explain.py`: Defines the `quick_explain` tool for explaining Python code.

- **`agents/`**:
    - `ollama_agent.py`: Contains the `OllamaAgent` class, which is responsible for communicating with the Ollama model and orchestrating the use of tools.
    - `tool_executor.py`: A class responsible for executing the tools defined in the `tools/` directory.
    - `prompts.py`: Contains the system prompts used to instruct the Ollama model on how to use the available tools.

- **`tools/`**:
    - `code_analysis.py`: Implements tools for static code analysis using libraries like `ast`, `radon`, and `bandit`.
    - `code_execution.py`: Implements tools for executing and testing Python code.
    - `documentation.py`: Implements tools for searching documentation.
    - `git_operations.py`: Implements tools for interacting with Git repositories.
    - `performance.py`: Implements tools for code profiling and performance analysis.

- **`utils/`**:
    - `config.py`: Manages the application's configuration.
    - `logger.py`: Sets up a structured logger for the application.
    - `cache.py`: Provides caching functionality to improve performance.

## 4. Setup and Execution

There are two ways to set up and run the project:

**A. Using Docker (Recommended)**

1.  **Build and run the Docker container**:
    ```bash
    docker-compose up --build
    ```

**B. Running Locally**

1.  **Install dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```

2.  **Run the server**:
    ```bash
    uv run server.py
    ```

Once the server is running, it will be accessible on port 8080.

## 5. Usage

To use the tools, you can interact with the Gemini CLI.

-   **List available tools**:
    ```
    /mcp list
    ```

-   **Use a tool with a natural language prompt**:
    ```
    "Fais une code_review sur app.py"
    ```

-   **Use a tool with a slash command**:
    ```
    /revue_code_complete app.py
    ```

## 6. Extending the Project

The project is designed to be easily extensible. To add a new tool, you need to:

1.  **Implement the tool's logic**: Create a new Python file in the `tools/` directory and implement the tool's functionality. The tool should be a class with a `get_tool_definition()` method that returns a dictionary describing the tool, and an `execute()` method that performs the tool's action.

2.  **Expose the tool through the MCP server**: Create a new Python file in the `mcp_tools/` directory and define a new tool using the `@mcp.tool()` decorator. This new tool will call the underlying tool implemented in the `tools/` directory.

3.  **Update the `OllamaAgent`**: If necessary, update the `OllamaAgent` and the prompts in `agents/prompts.py` to make the agent aware of the new tool and how to use it.
