"""
Prompt Loader Utility for Multi-Agent System
Manages loading and accessing prompts from the prompts directory
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from ai_agent import Prompt, PromptTemplate

logger = logging.getLogger(__name__)

@dataclass
class PromptMetadata:
    """Metadata for prompts"""
    name: str
    category: str
    file_path: str
    variables: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0"
    last_modified: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

class PromptLoader:
    """Utility class for loading and managing prompts"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.system_prompts: Dict[str, str] = {}
        self.task_prompts: Dict[str, str] = {}
        self.templates: Dict[str, str] = {}
        self.examples: Dict[str, str] = {}
        self.metadata: Dict[str, PromptMetadata] = {}
        
        # Ensure prompts directory exists
        if not self.prompts_dir.exists():
            raise ValueError(f"Prompts directory not found: {self.prompts_dir}")
        
        # Load all prompts
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompts from the directory structure"""
        logger.info(f"Loading prompts from {self.prompts_dir}")
        
        # Load system prompts
        system_dir = self.prompts_dir / "system"
        if system_dir.exists():
            self._load_prompts_from_dir(system_dir, self.system_prompts, "system")
        
        # Load task prompts
        task_dir = self.prompts_dir / "task"
        if task_dir.exists():
            self._load_prompts_from_dir(task_dir, self.task_prompts, "task")
        
        # Load templates
        templates_dir = self.prompts_dir / "templates"
        if templates_dir.exists():
            self._load_prompts_from_dir(templates_dir, self.templates, "template")
        
        # Load examples
        examples_dir = self.prompts_dir / "examples"
        if examples_dir.exists():
            self._load_prompts_from_dir(examples_dir, self.examples, "example")
        
        logger.info(f"Loaded {len(self.system_prompts)} system prompts, "
                   f"{len(self.task_prompts)} task prompts, "
                   f"{len(self.templates)} templates, "
                   f"{len(self.examples)} examples")
    
    def _load_prompts_from_dir(self, directory: Path, storage: Dict[str, str], category: str):
        """Load prompts from a specific directory"""
        for file_path in directory.glob("*.md"):
            try:
                name = file_path.stem
                content = file_path.read_text(encoding='utf-8')
                storage[name] = content
                
                # Create metadata
                variables = self._extract_variables(content)
                metadata = PromptMetadata(
                    name=name,
                    category=category,
                    file_path=str(file_path),
                    variables=variables,
                    description=self._extract_description(content),
                    last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                    tags=self._extract_tags(content)
                )
                self.metadata[name] = metadata
                
                logger.debug(f"Loaded {category} prompt: {name}")
                
            except Exception as e:
                logger.error(f"Error loading prompt from {file_path}: {e}")
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variables from prompt content"""
        import re
        variables = re.findall(r'\{([^}]+)\}', content)
        return list(set(variables))
    
    def _extract_description(self, content: str) -> str:
        """Extract description from prompt content"""
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                return line.strip('# ').strip()
        return ""
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from prompt content"""
        # Simple implementation - you can enhance this
        tags = []
        if "analysis" in content.lower():
            tags.append("analysis")
        if "research" in content.lower():
            tags.append("research")
        if "coordination" in content.lower():
            tags.append("coordination")
        return tags
    
    def get_system_prompt(self, name: str) -> Optional[str]:
        """Get a system prompt by name"""
        return self.system_prompts.get(name)
    
    def get_task_prompt(self, name: str) -> Optional[str]:
        """Get a task prompt by name"""
        return self.task_prompts.get(name)
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def get_example(self, name: str) -> Optional[str]:
        """Get an example by name"""
        return self.examples.get(name)
    
    def create_prompt_template(self, name: str, template_type: str = "task") -> Optional[PromptTemplate]:
        """Create a PromptTemplate object from loaded prompt"""
        content = None
        
        if template_type == "system":
            content = self.get_system_prompt(name)
        elif template_type == "task":
            content = self.get_task_prompt(name)
        elif template_type == "template":
            content = self.get_template(name)
        
        if content:
            metadata = self.metadata.get(name)
            variables = metadata.variables if metadata else []
            return PromptTemplate(name, content, variables)
        
        return None
    
    def create_prompt(self, template_name: str, template_type: str = "task", **kwargs) -> Optional[Prompt]:
        """Create a Prompt object from template with variables"""
        template = self.create_prompt_template(template_name, template_type)
        if template:
            return template.create_prompt(template_type, **kwargs)
        return None
    
    def list_prompts(self, category: str = None) -> List[str]:
        """List available prompts, optionally filtered by category"""
        if category == "system":
            return list(self.system_prompts.keys())
        elif category == "task":
            return list(self.task_prompts.keys())
        elif category == "template":
            return list(self.templates.keys())
        elif category == "example":
            return list(self.examples.keys())
        else:
            # Return all prompts
            all_prompts = []
            all_prompts.extend(self.system_prompts.keys())
            all_prompts.extend(self.task_prompts.keys())
            all_prompts.extend(self.templates.keys())
            all_prompts.extend(self.examples.keys())
            return all_prompts
    
    def get_prompt_metadata(self, name: str) -> Optional[PromptMetadata]:
        """Get metadata for a prompt"""
        return self.metadata.get(name)
    
    def search_prompts(self, query: str, category: str = None) -> List[str]:
        """Search prompts by name or content"""
        results = []
        
        prompts_to_search = {}
        if category == "system":
            prompts_to_search = self.system_prompts
        elif category == "task":
            prompts_to_search = self.task_prompts
        elif category == "template":
            prompts_to_search = self.templates
        elif category == "example":
            prompts_to_search = self.examples
        else:
            # Search all categories
            prompts_to_search.update(self.system_prompts)
            prompts_to_search.update(self.task_prompts)
            prompts_to_search.update(self.templates)
            prompts_to_search.update(self.examples)
        
        query_lower = query.lower()
        for name, content in prompts_to_search.items():
            if query_lower in name.lower() or query_lower in content.lower():
                results.append(name)
        
        return results
    
    def get_prompt_info(self, name: str) -> Dict[str, Any]:
        """Get comprehensive information about a prompt"""
        metadata = self.get_prompt_metadata(name)
        if not metadata:
            return {}
        
        info = {
            "name": metadata.name,
            "category": metadata.category,
            "description": metadata.description,
            "variables": metadata.variables,
            "version": metadata.version,
            "last_modified": metadata.last_modified.isoformat(),
            "tags": metadata.tags,
            "file_path": metadata.file_path
        }
        
        # Add content preview
        if metadata.category == "system":
            content = self.get_system_prompt(name)
        elif metadata.category == "task":
            content = self.get_task_prompt(name)
        elif metadata.category == "template":
            content = self.get_template(name)
        elif metadata.category == "example":
            content = self.get_example(name)
        else:
            content = ""
        
        if content:
            # Get first 200 characters as preview
            info["preview"] = content[:200] + "..." if len(content) > 200 else content
        
        return info
    
    def reload_prompts(self):
        """Reload all prompts from disk"""
        logger.info("Reloading all prompts")
        self.system_prompts.clear()
        self.task_prompts.clear()
        self.templates.clear()
        self.examples.clear()
        self.metadata.clear()
        self._load_all_prompts()
    
    def export_prompts(self, output_file: str):
        """Export all prompts to a JSON file"""
        export_data = {
            "system_prompts": self.system_prompts,
            "task_prompts": self.task_prompts,
            "templates": self.templates,
            "examples": self.examples,
            "metadata": {
                name: {
                    "name": meta.name,
                    "category": meta.category,
                    "file_path": meta.file_path,
                    "variables": meta.variables,
                    "description": meta.description,
                    "version": meta.version,
                    "last_modified": meta.last_modified.isoformat(),
                    "tags": meta.tags
                }
                for name, meta in self.metadata.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported prompts to {output_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded prompts"""
        stats = {
            "total_prompts": len(self.metadata),
            "system_prompts": len(self.system_prompts),
            "task_prompts": len(self.task_prompts),
            "templates": len(self.templates),
            "examples": len(self.examples),
            "total_variables": sum(len(meta.variables) for meta in self.metadata.values()),
            "categories": {
                "system": len(self.system_prompts),
                "task": len(self.task_prompts),
                "template": len(self.templates),
                "example": len(self.examples)
            }
        }
        
        return stats

# Convenience functions
def load_system_prompt(name: str, prompts_dir: str = "prompts") -> Optional[str]:
    """Quick function to load a system prompt"""
    loader = PromptLoader(prompts_dir)
    return loader.get_system_prompt(name)

def load_task_prompt(name: str, prompts_dir: str = "prompts") -> Optional[str]:
    """Quick function to load a task prompt"""
    loader = PromptLoader(prompts_dir)
    return loader.get_task_prompt(name)

def create_prompt_from_template(template_name: str, template_type: str = "task", 
                               prompts_dir: str = "prompts", **kwargs) -> Optional[Prompt]:
    """Quick function to create a prompt from template"""
    loader = PromptLoader(prompts_dir)
    return loader.create_prompt(template_name, template_type, **kwargs)

# Example usage
if __name__ == "__main__":
    # Create prompt loader
    loader = PromptLoader()
    
    # Print statistics
    stats = loader.get_statistics()
    print("Prompt Statistics:")
    print(f"Total prompts: {stats['total_prompts']}")
    print(f"System prompts: {stats['system_prompts']}")
    print(f"Task prompts: {stats['task_prompts']}")
    print(f"Templates: {stats['templates']}")
    print(f"Examples: {stats['examples']}")
    
    # List available prompts
    print("\nAvailable System Prompts:")
    for prompt in loader.list_prompts("system"):
        print(f"  - {prompt}")
    
    print("\nAvailable Task Prompts:")
    for prompt in loader.list_prompts("task"):
        print(f"  - {prompt}")
    
    # Example of loading and using a prompt
    analyst_prompt = loader.get_system_prompt("analyst")
    if analyst_prompt:
        print(f"\nAnalyst prompt loaded: {len(analyst_prompt)} characters")
    
    # Example of creating a prompt from template
    data_analysis_template = loader.create_prompt_template("data_analysis", "task")
    if data_analysis_template:
        print(f"\nData analysis template loaded with {len(data_analysis_template.variables)} variables") 