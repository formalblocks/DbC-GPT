import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class AssistantConfig:
    """Configuration for OpenAI assistants."""
    assistant_ids: Dict[str, str]
    
@dataclass
class ContractConfig:
    """Configuration for contract templates and specifications."""
    interface_paths: Dict[str, str]
    eip_paths: Dict[str, str]
    reference_spec_paths: Dict[str, str]
    
@dataclass
class VerifierConfig:
    """Configuration for verification settings."""
    max_iterations_per_function: int = 10
    max_retries: int = 5
    verification_timeout: int = 60  # seconds

class ConfigManager:
    """
    Manages configuration for the verifier.
    
    This class handles loading configuration from files and environment variables,
    and provides access to configuration values.
    """
    
    DEFAULT_CONFIG_PATH = "../config/default_config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to a JSON configuration file. If None, uses the default.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self._assistant_config = self._load_assistant_config()
        self._contract_config = self._load_contract_config()
        self._verifier_config = self._load_verifier_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the full configuration from file."""
        if not os.path.exists(self.config_path):
            logging.warning(f"Config file {self.config_path} not found. Using default values.")
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}
    
    def _load_assistant_config(self) -> AssistantConfig:
        """Load the assistant configuration."""
        assistant_ids = self.config.get('assistant_ids', {})
        # Could also load from environment variables or other sources
        return AssistantConfig(assistant_ids=assistant_ids)
    
    def _load_contract_config(self) -> ContractConfig:
        """Load the contract configuration."""
        interface_paths = self.config.get('interface_paths', {})
        eip_paths = self.config.get('eip_paths', {})
        reference_spec_paths = self.config.get('reference_spec_paths', {})
        return ContractConfig(
            interface_paths=interface_paths,
            eip_paths=eip_paths,
            reference_spec_paths=reference_spec_paths
        )
    
    def _load_verifier_config(self) -> VerifierConfig:
        """Load the verifier configuration."""
        verifier_config = self.config.get('verifier', {})
        return VerifierConfig(
            max_iterations_per_function=verifier_config.get('max_iterations_per_function', 10),
            max_retries=verifier_config.get('max_retries', 5),
            verification_timeout=verifier_config.get('verification_timeout', 60)
        )
    
    @property
    def assistant(self) -> AssistantConfig:
        """Get the assistant configuration."""
        return self._assistant_config
    
    @property
    def contract(self) -> ContractConfig:
        """Get the contract configuration."""
        return self._contract_config
    
    @property
    def verifier(self) -> VerifierConfig:
        """Get the verifier configuration."""
        return self._verifier_config
    
    def get_assistant_id(self, key: str) -> str:
        """
        Get an assistant ID by key.
        
        Args:
            key: The key for the assistant ID.
            
        Returns:
            The assistant ID.
            
        Raises:
            ValueError: If the key is not found.
        """
        if key not in self.assistant.assistant_ids:
            raise ValueError(f"Assistant ID for '{key}' not found in configuration.")
        return self.assistant.assistant_ids[key]
    
    def get_interface_path(self, contract_type: str) -> str:
        """
        Get the interface path for a contract type.
        
        Args:
            contract_type: The contract type (e.g., 'erc20').
            
        Returns:
            The path to the interface file.
            
        Raises:
            ValueError: If the contract type is not found.
        """
        if contract_type not in self.contract.interface_paths:
            raise ValueError(f"Interface path for '{contract_type}' not found in configuration.")
        return self.contract.interface_paths[contract_type] 