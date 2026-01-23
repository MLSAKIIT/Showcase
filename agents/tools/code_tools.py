"""
Code Modification Tools for Agno Agents.

Provides agents with capabilities to modify source code files,
update CSS variables, edit JSON, and make targeted code changes.
"""

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from agno.tools import Toolkit


class CodeModificationTools(Toolkit):
    """
    Toolkit for modifying source code files.
    
    Enables agents to make targeted code modifications including:
    - Find and replace text
    - Update CSS variables
    - Modify JSON/JS config files
    - Insert code at specific locations
    - Update TypeScript/JavaScript files
    """
    
    name = "code_modification_tools"
    
    def __init__(self, base_dir: Optional[str] = None):
        super().__init__()
        
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Register tools
        self.register(self.find_and_replace)
        self.register(self.update_css_variable)
        self.register(self.update_json_file)
        self.register(self.insert_code_after)
        self.register(self.insert_code_before)
        self.register(self.update_tailwind_colors)
        self.register(self.replace_in_file)
        self.register(self.append_to_file)
    
    def find_and_replace(
        self, 
        file_path: str, 
        find: str, 
        replace: str,
        count: int = -1
    ) -> str:
        """
        Find and replace text in a file.
        
        Args:
            file_path: Path to the file
            find: Text to find
            replace: Text to replace with
            count: Number of replacements (-1 for all)
            
        Returns:
            Success message with replacement count
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        try:
            content = path.read_text(encoding="utf-8")
            
            if count == -1:
                new_content = content.replace(find, replace)
                replacements = content.count(find)
            else:
                new_content = content.replace(find, replace, count)
                replacements = min(count, content.count(find))
            
            if new_content == content:
                return f"No matches found for: {find[:50]}..."
            
            path.write_text(new_content, encoding="utf-8")
            return f"Replaced {replacements} occurrence(s) in {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def update_css_variable(
        self, 
        file_path: str, 
        variable_name: str, 
        new_value: str
    ) -> str:
        """
        Update a CSS custom property (variable) in a CSS file.
        
        Args:
            file_path: Path to CSS file
            variable_name: Variable name (with or without --)
            new_value: New value for the variable
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        # Ensure variable name has -- prefix
        if not variable_name.startswith("--"):
            variable_name = f"--{variable_name}"
        
        try:
            content = path.read_text(encoding="utf-8")
            
            # Pattern to match CSS variable declaration
            pattern = rf"({re.escape(variable_name)}\s*:\s*)([^;]+)(;)"
            
            def replacer(match):
                return f"{match.group(1)}{new_value}{match.group(3)}"
            
            new_content, count = re.subn(pattern, replacer, content)
            
            if count == 0:
                return f"CSS variable not found: {variable_name}"
            
            path.write_text(new_content, encoding="utf-8")
            return f"Updated {variable_name} to {new_value}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def update_json_file(
        self, 
        file_path: str, 
        updates: Dict[str, Any]
    ) -> str:
        """
        Update specific keys in a JSON file.
        
        Args:
            file_path: Path to JSON file
            updates: Dictionary of keys to update (supports dot notation)
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            
            # Apply updates with dot notation support
            for key, value in updates.items():
                self._set_nested(data, key.split("."), value)
            
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return f"Updated {len(updates)} key(s) in {file_path}"
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def insert_code_after(
        self, 
        file_path: str, 
        after_line: str, 
        code: str
    ) -> str:
        """
        Insert code after a specific line.
        
        Args:
            file_path: Path to file
            after_line: Line to insert after (partial match)
            code: Code to insert
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            
            for i, line in enumerate(lines):
                if after_line in line:
                    # Preserve indentation
                    indent = len(line) - len(line.lstrip())
                    indented_code = "\n".join(
                        " " * indent + l if l.strip() else l 
                        for l in code.splitlines()
                    )
                    lines.insert(i + 1, indented_code + "\n")
                    
                    path.write_text("".join(lines), encoding="utf-8")
                    return f"Inserted code after line {i + 1}"
            
            return f"Line not found: {after_line[:50]}..."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def insert_code_before(
        self, 
        file_path: str, 
        before_line: str, 
        code: str
    ) -> str:
        """
        Insert code before a specific line.
        
        Args:
            file_path: Path to file
            before_line: Line to insert before (partial match)
            code: Code to insert
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            
            for i, line in enumerate(lines):
                if before_line in line:
                    indent = len(line) - len(line.lstrip())
                    indented_code = "\n".join(
                        " " * indent + l if l.strip() else l 
                        for l in code.splitlines()
                    )
                    lines.insert(i, indented_code + "\n")
                    
                    path.write_text("".join(lines), encoding="utf-8")
                    return f"Inserted code before line {i + 1}"
            
            return f"Line not found: {before_line[:50]}..."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def update_tailwind_colors(
        self, 
        config_path: str, 
        colors: Dict[str, str]
    ) -> str:
        """
        Update colors in a Tailwind CSS config file.
        
        Args:
            config_path: Path to tailwind.config.js
            colors: Dictionary of color names to hex values
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(config_path)
        
        if not path.exists():
            return f"Error: File not found: {config_path}"
        
        try:
            content = path.read_text(encoding="utf-8")
            
            for color_name, color_value in colors.items():
                # Pattern for Tailwind color in theme.colors or theme.extend.colors
                patterns = [
                    rf"(['\"]?{color_name}['\"]?\s*:\s*)['\"]#[0-9a-fA-F]+['\"]",
                    rf"(['\"]?{color_name}['\"]?\s*:\s*)['\"][^'\"]+['\"]",
                ]
                
                for pattern in patterns:
                    content = re.sub(
                        pattern, 
                        f'\\1"{color_value}"', 
                        content
                    )
            
            path.write_text(content, encoding="utf-8")
            return f"Updated {len(colors)} color(s) in Tailwind config"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def replace_in_file(
        self, 
        file_path: str, 
        pattern: str, 
        replacement: str,
        is_regex: bool = False
    ) -> str:
        """
        Replace content in file using string or regex pattern.
        
        Args:
            file_path: Path to file
            pattern: Pattern to match (string or regex)
            replacement: Replacement text
            is_regex: Whether pattern is a regex
            
        Returns:
            Success message with replacement count
        """
        path = self._resolve_path(file_path)
        
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        try:
            content = path.read_text(encoding="utf-8")
            
            if is_regex:
                new_content, count = re.subn(pattern, replacement, content)
            else:
                count = content.count(pattern)
                new_content = content.replace(pattern, replacement)
            
            if new_content == content:
                return f"No matches found"
            
            path.write_text(new_content, encoding="utf-8")
            return f"Replaced {count} occurrence(s)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def append_to_file(self, file_path: str, content: str) -> str:
        """
        Append content to the end of a file.
        
        Args:
            file_path: Path to file
            content: Content to append
            
        Returns:
            Success message or error
        """
        path = self._resolve_path(file_path)
        
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Appended content to {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base directory."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / path
    
    def _set_nested(self, data: dict, keys: List[str], value: Any) -> None:
        """Set a nested dictionary value using a list of keys."""
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
