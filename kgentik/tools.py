"""
KgentikTools - Framework-agnostic tool resolver for Kgentik platform

This module provides seamless tool resolution from kgentik.yaml configuration,
supporting both local development and deployed environments.
"""
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import importlib.util
import sys


class KgentikTools:
    """
    Framework-agnostic tool resolver for Kgentik platform.
    
    Automatically detects and loads tools from kgentik.yaml configuration.
    Works seamlessly in both local development and deployed environments.
    
    Example:
        >>> from kgentik.tools import KgentikTools
        >>> tools = KgentikTools()
        >>> tool_list = tools.get_tools()
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize KgentikTools with optional config path.
        
        Args:
            config_path: Path to kgentik.yaml file. If None, auto-detects.
        """
        self.config_path = config_path or self._find_config()
        self._tools_cache: Dict[str, Any] = {}
        
        if not self.config_path:
            raise FileNotFoundError(
                "No kgentik.yaml found. Please ensure you're in a Kgentik project directory "
                "or provide a config_path."
            )
    
    def _find_config(self) -> Optional[str]:
        """Find kgentik.yaml in current or parent directories."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            config = parent / "kgentik.yaml"
            if config.exists():
                return str(config)
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse kgentik.yaml configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse kgentik.yaml: {e}")
    
    def _load_tool_from_file(self, file_path: str, tool_name: str) -> Any:
        """
        Load a tool from a Python file.
        
        Args:
            file_path: Path to the tool file
            tool_name: Name of the tool to load
            
        Returns:
            The tool function/object
        """
        # Resolve relative to config directory
        config_dir = Path(self.config_path).parent
        tool_path = config_dir / file_path
        
        if not tool_path.exists():
            raise FileNotFoundError(f"Tool file not found: {tool_path}")
        
        # Import the tool module
        spec = importlib.util.spec_from_file_location(tool_name, tool_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load module from {tool_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for the tool function/class
        # Convention: tool name or default export
        if hasattr(module, tool_name):
            return getattr(module, tool_name)
        elif hasattr(module, "tool"):
            return module.tool
        else:
            # Try to find @tool decorated functions or any callable
            for attr_name in dir(module):
                if attr_name.startswith('_'):
                    continue
                attr = getattr(module, attr_name)
                if callable(attr):
                    return attr
        
        raise ValueError(f"Could not find tool '{tool_name}' in {file_path}")
    
    def _load_tool_from_registry(self, tool_name: str) -> Any:
        """
        Load a tool from the tools registry (for deployed environments).
        
        Args:
            tool_name: Name of the tool to load
            
        Returns:
            The tool function/object
        """
        try:
            # Try to import from tools registry
            from tools import get_available_tools
            tools = get_available_tools()
            
            # Find tool by name
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == tool_name:
                    return tool
                elif hasattr(tool, '__name__') and tool.__name__ == tool_name:
                    return tool
            
            # If not found by name, try to import directly
            try:
                tool_module = __import__(f"tools.tool_{tool_name.replace('-', '_')}", fromlist=[tool_name])
                return getattr(tool_module, tool_name, None)
            except ImportError:
                pass
            
            raise ValueError(f"Tool '{tool_name}' not found in registry")
            
        except ImportError:
            raise ImportError("Tools registry not available. Ensure you're in a deployed environment.")
    
    def get_tools(self) -> List[Any]:
        """
        Get all tools based on kgentik.yaml configuration.
        
        Returns:
            List of tool functions/objects compatible with the framework
        """
        config = self._load_config()
        tools = []
        tool_defs = config.get("tools", [])
        
        for tool_def in tool_defs:
            tool_name = tool_def["name"]
            source = tool_def.get("source", "local")
            
            # Check cache first
            cache_key = f"{tool_name}:{source}"
            if cache_key in self._tools_cache:
                tools.append(self._tools_cache[cache_key])
                continue
            
            try:
                if source == "local":
                    # Load from local file
                    file_path = tool_def.get("file")
                    if not file_path:
                        raise ValueError(f"Local tool '{tool_name}' missing 'file' field")
                    
                    tool = self._load_tool_from_file(file_path, tool_name)
                    
                elif source in ["team", "community"]:
                    # In deployed environment, these are available via tools registry
                    # In local dev, we might skip or use mocks
                    try:
                        tool = self._load_tool_from_registry(tool_name)
                    except ImportError:
                        print(f"Warning: Skipping {source} tool '{tool_name}' - not available locally")
                        continue
                        
                else:
                    raise ValueError(f"Unknown tool source: {source}")
                
                # Cache the tool
                self._tools_cache[cache_key] = tool
                tools.append(tool)
                
            except Exception as e:
                print(f"Warning: Failed to load tool '{tool_name}': {e}")
                continue
        
        return tools
    
    def __iter__(self):
        """Make it iterable."""
        return iter(self.get_tools())
    
    def __len__(self):
        """Support len()."""
        return len(self.get_tools())
    
    def __repr__(self):
        """String representation."""
        return f"KgentikTools(config_path='{self.config_path}')"


# TODO: Future extensions
# - CLI tools (kgentik deploy, kgentik test, kgentik init)
# - Testing utilities for agents
# - Deployment helpers
# - Multi-framework adapters (LangGraph, LlamaIndex, CrewAI, etc.)
# - Tool validation and type checking
# - Hot-reloading for development
