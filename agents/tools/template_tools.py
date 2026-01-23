"""
Template Registry Tools for Agno Agents.

Provides agents with access to template information
and selection capabilities.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from agno.tools import Toolkit


class TemplateRegistryTools(Toolkit):
    """
    Toolkit for working with the template registry.
    
    Enables agents to:
    - List available templates
    - Get template details
    - Find templates by criteria
    - Get template data file paths
    """
    
    name = "template_registry_tools"
    
    def __init__(self, templates_dir: Optional[str] = None):
        super().__init__()
        
        if templates_dir:
            self.templates_dir = Path(templates_dir).resolve()
        else:
            self.templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"
        
        self.registry_path = self.templates_dir / "registry.json"
        self._registry_cache: Optional[Dict] = None
        
        # Register tools
        self.register(self.list_templates)
        self.register(self.get_template)
        self.register(self.find_templates_by_role)
        self.register(self.find_templates_by_features)
        self.register(self.get_template_data_file)
        self.register(self.get_template_path)
    
    def _load_registry(self) -> Dict:
        """Load and cache the template registry."""
        if self._registry_cache is None:
            if self.registry_path.exists():
                self._registry_cache = json.loads(
                    self.registry_path.read_text(encoding="utf-8")
                )
            else:
                self._registry_cache = {"templates": []}
        return self._registry_cache
    
    def list_templates(self) -> str:
        """
        List all available templates.
        
        Returns:
            JSON list of template summaries
        """
        registry = self._load_registry()
        templates = registry.get("templates", [])
        
        summaries = []
        for t in templates:
            summaries.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "framework": t.get("framework"),
                "type": t.get("type"),
                "features": t.get("features", []),
            })
        
        return json.dumps(summaries, indent=2)
    
    def get_template(self, template_id: str) -> str:
        """
        Get full details for a specific template.
        
        Args:
            template_id: Template ID (e.g., "one_temp")
            
        Returns:
            JSON object with template details
        """
        registry = self._load_registry()
        
        for t in registry.get("templates", []):
            if t.get("id") == template_id:
                return json.dumps(t, indent=2)
        
        return f"Template not found: {template_id}"
    
    def find_templates_by_role(self, role: str) -> str:
        """
        Find templates recommended for a specific role.
        
        Args:
            role: User role (e.g., "developer", "designer")
            
        Returns:
            JSON list of matching template IDs
        """
        registry = self._load_registry()
        criteria = registry.get("selectionCriteria", {})
        by_role = criteria.get("byRole", {})
        
        role_lower = role.lower()
        
        # Check for exact and partial matches
        for role_key, template_ids in by_role.items():
            if role_key in role_lower or role_lower in role_key:
                return json.dumps({
                    "role": role_key,
                    "recommended_templates": template_ids
                }, indent=2)
        
        return json.dumps({
            "role": role,
            "recommended_templates": [],
            "message": "No specific recommendations, using fallback"
        }, indent=2)
    
    def find_templates_by_features(self, features: List[str]) -> str:
        """
        Find templates that have specific features.
        
        Args:
            features: List of required features
            
        Returns:
            JSON list of matching templates
        """
        registry = self._load_registry()
        templates = registry.get("templates", [])
        
        matching = []
        for t in templates:
            template_features = set(t.get("features", []))
            required = set(features)
            
            if required.issubset(template_features):
                matching.append({
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "features": list(template_features),
                    "match_score": len(required & template_features)
                })
        
        # Sort by match score
        matching.sort(key=lambda x: x["match_score"], reverse=True)
        
        return json.dumps(matching, indent=2)
    
    def get_template_data_file(self, template_id: str) -> str:
        """
        Get the path to a template's data file.
        
        Args:
            template_id: Template ID
            
        Returns:
            Path to data file, or error message
        """
        template_path = self.templates_dir / template_id
        
        if not template_path.exists():
            return f"Template not found: {template_id}"
        
        # Common data file locations
        data_files = [
            "assets/lib/data.tsx",  # one_temp
            "data/data.tsx",        # six_temp
            "config.js",            # three_temp
            "src/data/portfolio.json",
            "data/portfolio.json",
        ]
        
        for data_file in data_files:
            if (template_path / data_file).exists():
                return str(template_path / data_file)
        
        return f"No data file found for template: {template_id}"
    
    def get_template_path(self, template_id: str) -> str:
        """
        Get the full path to a template directory.
        
        Args:
            template_id: Template ID
            
        Returns:
            Absolute path to template directory
        """
        template_path = self.templates_dir / template_id
        
        if template_path.exists():
            return str(template_path)
        
        return f"Template not found: {template_id}"
