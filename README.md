# Kgentik SDK

Seamless tool resolution and agent development for the Kgentik platform.

## Installation

For local development:

```bash
pip install kgentik
```

**Note**: In deployed environments, the SDK is automatically injected and no installation is required.

## Quick Start

The KgentikTools wrapper automatically detects and loads tools from your `kgentik.yaml` configuration:

```python
from kgentik.tools import KgentikTools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Initialize tools - automatically reads from kgentik.yaml
kgentik_tools = KgentikTools()
tools = kgentik_tools.get_tools()

# Create your agent
model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, tools)
```

## Configuration

Define your tools in `kgentik.yaml`:

```yaml
tools:
  - name: "csv_parser"
    source: "local"
    file: "tools/csv_parser.py"
    description: "Parse CSV data"
  
  - name: "web-scraper"
    source: "community"
    description: "Scrape web pages"
  
  - name: "email-sender"
    source: "team"
    description: "Send emails"
```

### Tool Sources

- **`local`**: Tools you develop locally (requires `file` field)
- **`team`**: Tools shared within your team
- **`community`**: Public tools from the community

## How It Works

### Local Development

1. Place your `kgentik.yaml` in your project root
2. Create local tools in the `tools/` directory
3. Use `KgentikTools()` to automatically load all configured tools
4. Same code works when deployed!

### Deployed Environment

1. Platform automatically injects the SDK during deployment
2. Local tools are packaged alongside your agent
3. Team/community tools are fetched and made available
4. `KgentikTools()` resolves all tools seamlessly

## Examples

### Basic Usage

```python
from kgentik.tools import KgentikTools

# Auto-detects kgentik.yaml and loads all tools
tools = KgentikTools().get_tools()
```

### Custom Config Path

```python
from kgentik.tools import KgentikTools

# Specify custom config path
tools = KgentikTools(config_path="./custom-config.yaml").get_tools()
```

### LangGraph Integration

```python
from kgentik.tools import KgentikTools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

kgentik_tools = KgentikTools()
tools = kgentik_tools.get_tools()

model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, tools)

# Use your agent
result = agent.invoke({"messages": [("user", "Hello!")]})
```

### Custom Agent Implementation

```python
from kgentik.tools import KgentikTools
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

# Load tools
kgentik_tools = KgentikTools()
tools = kgentik_tools.get_tools()

# Create custom workflow
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)

app = workflow.compile()
```

## Error Handling

The SDK provides clear error messages for common issues:

```python
# Missing kgentik.yaml
FileNotFoundError: No kgentik.yaml found. Please ensure you're in a Kgentik project directory or provide a config_path.

# Missing tool file
FileNotFoundError: Tool file not found: /path/to/tools/missing_tool.py

# Invalid tool source
ValueError: Unknown tool source: invalid_source
```

## Troubleshooting

### Tool Not Found

1. Check that your tool is defined in `kgentik.yaml`
2. Verify the `file` path is correct for local tools
3. Ensure the tool function is properly exported

### Import Errors

1. Make sure you're in a Kgentik project directory
2. Verify `kgentik.yaml` exists in current or parent directory
3. Check that required dependencies are installed

### Deployment Issues

1. Ensure your agent uses `KgentikTools()` (not manual imports)
2. Verify all tools are properly configured in `kgentik.yaml`
3. Check that team/community tools exist and are accessible

## Future Roadmap

### Planned Features

- **CLI Tools**: `kgentik deploy`, `kgentik test`, `kgentik init`
- **Testing Utilities**: Built-in testing framework for agents
- **Deployment Helpers**: Streamlined deployment process
- **Multi-Framework Support**: Enhanced support for LlamaIndex, CrewAI, etc.
- **Tool Validation**: Type checking and validation for tools
- **Hot Reloading**: Development mode with automatic reloading

### Contributing

The SDK is part of the Kgentik platform. For contributions and issues, please visit our [GitHub repository](https://github.com/kgentik/kgentik).

## License

MIT License - see LICENSE file for details.
