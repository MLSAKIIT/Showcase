"""
File System Tools for Agno Agents.

Provides agents with file read/write capabilities for template customization.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List
from agno.tools import Toolkit


class FileSystemTools(Toolkit):
    """
    Toolkit for file system operations.
    
    Allows agents to read, write, copy, and manage files
    within the templates and output directories.
    """
    
    name = "file_system_tools"
    
    def __init__(
        self,
        base_dir: Optional[str] = None,
        templates_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        super().__init__()
        
        # Resolve base directory
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            # Default to project root (3 levels up from this file)
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        
        self.templates_dir = Path(templates_dir) if templates_dir else self.base_dir / "templates"
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "output"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Register tools
        self.register(self.read_file)
        self.register(self.write_file)
        self.register(self.list_directory)
        self.register(self.copy_template)
        self.register(self.file_exists)
        self.register(self.create_directory)
    
    def read_file(self, path: str) -> str:
        """
        Read the contents of a file.
        
        Args:
            path: Relative path from base directory, or absolute path
            
        Returns:
            File contents as string
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            path: Relative path from output directory, or absolute path
            content: Content to write
            
        Returns:
            Success message or error
        """
        file_path = self._resolve_output_path(path)
        
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote to: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def list_directory(self, path: str = "") -> str:
        """
        List contents of a directory.
        
        Args:
            path: Relative path from base directory
            
        Returns:
            JSON list of files and directories
        """
        dir_path = self._resolve_path(path) if path else self.base_dir
        
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"
        
        if not dir_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        try:
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            return json.dumps(items, indent=2)
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def copy_template(self, template_id: str, output_name: Optional[str] = None) -> str:
        """
        Copy a template to the output directory for customization.
        
        Args:
            template_id: Template ID (e.g., "one_temp")
            output_name: Optional custom name for output directory
            
        Returns:
            Path to the copied template
        """
        source = self.templates_dir / template_id
        
        if not source.exists():
            return f"Error: Template not found: {template_id}"
        
        dest_name = output_name or template_id
        dest = self.output_dir / dest_name
        
        try:
            # Remove existing if present
            if dest.exists():
                shutil.rmtree(dest)
            
            # Copy template
            shutil.copytree(source, dest)
            return f"Template copied to: {dest}"
        except Exception as e:
            return f"Error copying template: {str(e)}"
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: File path to check
            
        Returns:
            True if file exists
        """
        return self._resolve_path(path).exists()
    
    def create_directory(self, path: str) -> str:
        """
        Create a directory.
        
        Args:
            path: Directory path to create
            
        Returns:
            Success message or error
        """
        dir_path = self._resolve_output_path(path)
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return f"Directory created: {dir_path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base directory."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / path
    
    def _resolve_output_path(self, path: str) -> Path:
        """Resolve path relative to output directory."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.output_dir / path
