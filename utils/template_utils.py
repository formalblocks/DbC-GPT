#!/usr/bin/env python3

import os
from typing import Dict, List, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader

class TemplateManager:
    """Utility class for managing templates for ERC standards"""
    
    def __init__(self):
        """Initialize the template manager with paths to template files"""
        # Base paths for ERC templates
        self.template_paths = {
            "erc20": os.path.join("experiments", "solc_verify_generator", "ERC20", "templates"),
            "erc721": os.path.join("experiments", "solc_verify_generator", "ERC721", "templates"),
            "erc1155": os.path.join("experiments", "solc_verify_generator", "ERC1155", "templates")
        }
        
        # Implementation paths for each ERC
        self.implementation_paths = {
            "erc20": os.path.join("experiments", "solc_verify_generator", "ERC20", "imp"),
            "erc721": os.path.join("experiments", "solc_verify_generator", "ERC721", "imp"),
            "erc1155": os.path.join("experiments", "solc_verify_generator", "ERC1155", "imp")
        }
        
        # EIP specification files
        self.spec_paths = {
            "erc20": os.path.join("experiments", "solc_verify_generator", "ERC20", "eip.md"),
            "erc721": os.path.join("experiments", "solc_verify_generator", "ERC721", "eip.md"),
            "erc1155": os.path.join("experiments", "solc_verify_generator", "ERC1155", "eip.md")
        }
        
        # Initialize Jinja2 environment
        self.env = Environment(loader=FileSystemLoader("."))
        
        # Cache for loaded templates
        self._template_cache = {}
    
    def get_template(self, erc_type: str, template_name: str = "imp_spec_merge.template") -> Template:
        """
        Get a Jinja2 template for the specified ERC standard
        
        Args:
            erc_type: ERC standard type (erc20, erc721, erc1155)
            template_name: Name of the template file
            
        Returns:
            Jinja2 template object
        """
        cache_key = f"{erc_type}_{template_name}"
        
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        template_path = os.path.join(self.template_paths[erc_type], template_name)
        
        with open(template_path, 'r') as f:
            template_str = f.read()
            template = Template(template_str)
            self._template_cache[cache_key] = template
            return template
    
    def get_eip_spec(self, erc_type: str) -> str:
        """
        Get the EIP specification for an ERC standard
        
        Args:
            erc_type: ERC standard type (erc20, erc721, erc1155)
            
        Returns:
            EIP specification as a string
        """
        spec_path = self.spec_paths[erc_type]
        
        with open(spec_path, 'r') as f:
            return f.read()
    
    def get_implementation_path(self, erc_type: str, filename: str) -> str:
        """
        Get the path to an implementation file
        
        Args:
            erc_type: ERC standard type (erc20, erc721, erc1155)
            filename: Name of the implementation file
            
        Returns:
            Full path to the implementation file
        """
        return os.path.join(self.implementation_paths[erc_type], filename)
    
    def render_template(self, erc_type: str, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the provided context
        
        Args:
            erc_type: ERC standard type (erc20, erc721, erc1155)
            template_name: Name of the template file
            context: Dictionary of context variables for template rendering
            
        Returns:
            Rendered template as a string
        """
        template = self.get_template(erc_type, template_name)
        return template.render(**context)
    
    def create_jinja_environment(self, template_dir: Optional[str] = None) -> Environment:
        """
        Create a Jinja2 environment for rendering templates
        
        Args:
            template_dir: Optional directory for templates
            
        Returns:
            Jinja2 Environment object
        """
        if template_dir:
            return Environment(loader=FileSystemLoader(template_dir))
        else:
            # Use a loader that can find templates in any of our ERC directories
            search_paths = list(self.template_paths.values())
            return Environment(loader=FileSystemLoader(search_paths))
            
    def get_function_placeholders(self, erc_type: str) -> List[str]:
        """
        Get a list of function placeholder names in a template
        
        Args:
            erc_type: ERC standard type (erc20, erc721, erc1155)
            
        Returns:
            List of function placeholder names
        """
        # Predefined function placeholders for each ERC standard
        placeholder_mapping = {
            "erc20": [
                "totalSupply", "balanceOf", "transfer", "transferFrom", 
                "approve", "allowance"
            ],
            "erc721": [
                "balanceOf", "ownerOf", "safeTransferFrom3", "safeTransferFrom4",
                "transferFrom", "approve", "setApprovalForAll", 
                "getApproved", "isApprovedForAll"
            ],
            "erc1155": [
                "balanceOf", "balanceOfBatch", "setApprovalForAll", 
                "isApprovedForAll", "safeTransferFrom", "safeBatchTransferFrom"
            ]
        }
        
        return placeholder_mapping.get(erc_type, []) 