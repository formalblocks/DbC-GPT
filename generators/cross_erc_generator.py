#!/usr/bin/env python3

import os
import json
import random
from typing import Dict, List, Any, Tuple, Set
import re

class CrossERCGenerator:
    """Generator for cross-ERC verification examples"""
    
    def __init__(self):
        # Define cross-ERC interaction patterns
        self.interaction_patterns = {
            # ERC20 + ERC721
            ("erc20", "erc721"): [
                "token_purchase",  # Buy NFT with tokens
                "staking",         # Stake tokens to earn NFT rewards
                "fractional_nft",  # Tokenize NFT into fungible parts
                "royalty_payment"  # Pay royalties in tokens for NFT transfers
            ],
            
            # ERC20 + ERC1155
            ("erc20", "erc1155"): [
                "bundle_purchase",    # Buy ERC1155 tokens with ERC20
                "liquidity_pool",     # Provide liquidity with both token types
                "swap_mechanism",     # Swap between token types
                "subscription_model"  # Pay subscription fees in ERC20 for ERC1155 benefits
            ],
            
            # ERC721 + ERC1155
            ("erc721", "erc1155"): [
                "nft_bundling",       # Bundle NFTs with multi-tokens
                "upgrade_mechanism",  # Upgrade NFT using ERC1155 resources
                "inventory_system",   # NFT with ERC1155 inventory items
                "crafting_system"     # Craft NFTs from ERC1155 materials
            ],
            
            # ERC20 + ERC721 + ERC1155 (rarely needed)
            ("erc20", "erc721", "erc1155"): [
                "game_ecosystem",     # Complete game economy
                "dao_governance",     # Governance with multiple token types
                "metaverse_assets"    # Metaverse with various asset types
            ]
        }
        
        # Template snippets for different interaction types
        self.template_snippets = {
            # ERC20 + ERC721
            "token_purchase": """
    /// @notice Buy an NFT using ERC20 tokens
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - price || !success
    /// @notice postcondition _balances[nftSeller] == __verifier_old_uint(_balances[nftSeller]) + price || !success
    /// @notice postcondition _tokenOwner[tokenId] == msg.sender || !success
    /// @notice postcondition _ownedTokensCount[nftSeller] == __verifier_old_uint(_ownedTokensCount[nftSeller]) - 1 || !success
    /// @notice postcondition _ownedTokensCount[msg.sender] == __verifier_old_uint(_ownedTokensCount[msg.sender]) + 1 || !success
    function buyNFTWithTokens(uint256 tokenId, uint256 price) public returns (bool success) {
        address nftSeller = _tokenOwner[tokenId];
        require(nftSeller != address(0), "ERC721: owner query for nonexistent token");
        require(_balances[msg.sender] >= price, "ERC20: insufficient balance");
        
        // Transfer tokens to the seller
        _balances[msg.sender] = _balances[msg.sender] - price;
        _balances[nftSeller] = _balances[nftSeller] + price;
        emit Transfer(msg.sender, nftSeller, price);
        
        // Transfer NFT to the buyer
        _tokenOwner[tokenId] = msg.sender;
        _ownedTokensCount[nftSeller] = _ownedTokensCount[nftSeller] - 1;
        _ownedTokensCount[msg.sender] = _ownedTokensCount[msg.sender] + 1;
        emit Transfer(nftSeller, msg.sender, tokenId);
        
        return true;
    }
""",
            
            "staking": """
    /// @notice Stake ERC20 tokens to earn NFT rewards
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - amount || !success
    /// @notice postcondition _balances[address(this)] == __verifier_old_uint(_balances[address(this)]) + amount || !success
    /// @notice postcondition stakedAmount[msg.sender] == __verifier_old_uint(stakedAmount[msg.sender]) + amount || !success
    function stakeTokens(uint256 amount) public returns (bool success) {
        require(_balances[msg.sender] >= amount, "ERC20: insufficient balance");
        
        // Transfer tokens to the contract
        _balances[msg.sender] = _balances[msg.sender] - amount;
        _balances[address(this)] = _balances[address(this)] + amount;
        emit Transfer(msg.sender, address(this), amount);
        
        // Update staking record
        stakedAmount[msg.sender] = stakedAmount[msg.sender] + amount;
        
        return true;
    }
    
    /// @notice Claim NFT reward after staking
    /// @notice postcondition _tokenOwner[newTokenId] == msg.sender || !success
    /// @notice postcondition _ownedTokensCount[msg.sender] == __verifier_old_uint(_ownedTokensCount[msg.sender]) + 1 || !success
    /// @notice postcondition stakedAmount[msg.sender] >= minimumStake || !success
    function claimNFTReward() public returns (bool success) {
        uint256 minimumStake = 100 * (10 ** 18); // 100 tokens
        require(stakedAmount[msg.sender] >= minimumStake, "Insufficient staked amount");
        
        // Mint new NFT to the staker
        uint256 newTokenId = _getNextTokenId();
        _tokenOwner[newTokenId] = msg.sender;
        _ownedTokensCount[msg.sender] = _ownedTokensCount[msg.sender] + 1;
        emit Transfer(address(0), msg.sender, newTokenId);
        
        return true;
    }
""",

            # ERC20 + ERC1155
            "bundle_purchase": """
    /// @notice Buy ERC1155 tokens with ERC20 tokens
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - price || !success
    /// @notice postcondition _balances[seller] == __verifier_old_uint(_balances[seller]) + price || !success
    /// @notice postcondition _balances[msg.sender][id] == __verifier_old_uint(_balances[msg.sender][id]) + amount || !success
    /// @notice postcondition _balances[seller][id] == __verifier_old_uint(_balances[seller][id]) - amount || !success
    function buyMultiTokens(address seller, uint256 id, uint256 amount, uint256 price) public returns (bool success) {
        require(_balances[msg.sender] >= price, "ERC20: insufficient balance");
        require(_balances[seller][id] >= amount, "ERC1155: insufficient balance");
        
        // Transfer ERC20 tokens to seller
        _balances[msg.sender] = _balances[msg.sender] - price;
        _balances[seller] = _balances[seller] + price;
        emit Transfer(msg.sender, seller, price);
        
        // Transfer ERC1155 tokens to buyer
        _balances[seller][id] = _balances[seller][id] - amount;
        _balances[msg.sender][id] = _balances[msg.sender][id] + amount;
        emit TransferSingle(msg.sender, seller, msg.sender, id, amount);
        
        return true;
    }
""",

            # ERC721 + ERC1155
            "nft_bundling": """
    /// @notice Bundle an NFT with ERC1155 items
    /// @notice postcondition _tokenOwner[tokenId] == address(this) || !success
    /// @notice postcondition _ownedTokensCount[msg.sender] == __verifier_old_uint(_ownedTokensCount[msg.sender]) - 1 || !success
    /// @notice postcondition _ownedTokensCount[address(this)] == __verifier_old_uint(_ownedTokensCount[address(this)]) + 1 || !success
    /// @notice postcondition _balances[msg.sender][itemId] == __verifier_old_uint(_balances[msg.sender][itemId]) - itemAmount || !success
    /// @notice postcondition _balances[address(this)][itemId] == __verifier_old_uint(_balances[address(this)][itemId]) + itemAmount || !success
    /// @notice postcondition bundles[bundleId].owner == msg.sender || !success
    function createBundle(uint256 tokenId, uint256 itemId, uint256 itemAmount) public returns (uint256 bundleId) {
        require(_tokenOwner[tokenId] == msg.sender, "ERC721: not token owner");
        require(_balances[msg.sender][itemId] >= itemAmount, "ERC1155: insufficient balance");
        
        // Transfer NFT to contract
        address from = msg.sender;
        address to = address(this);
        _tokenOwner[tokenId] = to;
        _ownedTokensCount[from] = _ownedTokensCount[from] - 1;
        _ownedTokensCount[to] = _ownedTokensCount[to] + 1;
        emit Transfer(from, to, tokenId);
        
        // Transfer ERC1155 to contract
        _balances[msg.sender][itemId] = _balances[msg.sender][itemId] - itemAmount;
        _balances[address(this)][itemId] = _balances[address(this)][itemId] + itemAmount;
        emit TransferSingle(msg.sender, from, to, itemId, itemAmount);
        
        // Create bundle record
        bundleId = nextBundleId++;
        bundles[bundleId] = Bundle({
            owner: msg.sender,
            tokenId: tokenId,
            itemId: itemId,
            itemAmount: itemAmount
        });
        
        return bundleId;
    }
"""
        }

    def generate_cross_example(self, primary_erc: str, secondary_erc: str, index: int) -> Dict:
        """Generate a cross-ERC example involving two standards"""
        # Sort ERCs to find appropriate interaction pattern
        erc_pair = tuple(sorted([primary_erc, secondary_erc]))
        
        # Get possible interaction patterns
        if erc_pair in self.interaction_patterns:
            patterns = self.interaction_patterns[erc_pair]
            selected_pattern = random.choice(patterns)
        else:
            # Fallback if no direct match (shouldn't happen with our defined patterns)
            all_patterns = []
            for patterns_list in self.interaction_patterns.values():
                all_patterns.extend(patterns_list)
            selected_pattern = random.choice(all_patterns)
        
        # Get snippet for the selected pattern
        if selected_pattern in self.template_snippets:
            code_snippet = self.template_snippets[selected_pattern]
        else:
            # Generate generic cross interaction if pattern doesn't have a snippet
            code_snippet = self._generate_generic_cross_interaction(primary_erc, secondary_erc)
        
        # Create contract by combining the two ERC standards
        contract = self._create_cross_contract(primary_erc, secondary_erc, code_snippet, selected_pattern)
        
        # Create the example
        example = {
            "id": f"cross_{primary_erc}_{secondary_erc}_{index}",
            "category": "cross",
            "erc_type": primary_erc,  # Primary ERC type
            "secondary_erc": secondary_erc,
            "contract": contract,
            "pattern": selected_pattern
        }
        
        return example

    def _generate_generic_cross_interaction(self, primary_erc: str, secondary_erc: str) -> str:
        """Generate a generic cross-ERC interaction when no specific template is available"""
        # This is a fallback that creates a simple interaction between the two standards
        
        if primary_erc == "erc20" and secondary_erc == "erc721":
            return """
    /// @notice Generic ERC20-ERC721 interaction
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - amount || !success
    /// @notice postcondition _tokenOwner[tokenId] == msg.sender || !success
    function swapTokenForNFT(uint256 amount, uint256 tokenId) public returns (bool success) {
        require(_balances[msg.sender] >= amount, "ERC20: insufficient balance");
        address nftOwner = _tokenOwner[tokenId];
        require(nftOwner != address(0) && nftOwner != msg.sender, "Invalid NFT owner");
        
        // Transfer tokens
        _balances[msg.sender] = _balances[msg.sender] - amount;
        _balances[nftOwner] = _balances[nftOwner] + amount;
        
        // Transfer NFT
        _tokenOwner[tokenId] = msg.sender;
        _ownedTokensCount[nftOwner] = _ownedTokensCount[nftOwner] - 1;
        _ownedTokensCount[msg.sender] = _ownedTokensCount[msg.sender] + 1;
        
        return true;
    }
"""
        elif primary_erc == "erc20" and secondary_erc == "erc1155":
            return """
    /// @notice Generic ERC20-ERC1155 interaction
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - tokenAmount || !success
    /// @notice postcondition _balances[itemOwner] == __verifier_old_uint(_balances[itemOwner]) + tokenAmount || !success
    /// @notice postcondition _balances[itemOwner][id] == __verifier_old_uint(_balances[itemOwner][id]) - itemAmount || !success
    /// @notice postcondition _balances[msg.sender][id] == __verifier_old_uint(_balances[msg.sender][id]) + itemAmount || !success
    function buyMultiItems(address itemOwner, uint256 id, uint256 itemAmount, uint256 tokenAmount) public returns (bool success) {
        require(_balances[msg.sender] >= tokenAmount, "ERC20: insufficient balance");
        require(_balances[itemOwner][id] >= itemAmount, "ERC1155: insufficient balance");
        
        // Transfer tokens
        _balances[msg.sender] = _balances[msg.sender] - tokenAmount;
        _balances[itemOwner] = _balances[itemOwner] + tokenAmount;
        
        // Transfer items
        _balances[itemOwner][id] = _balances[itemOwner][id] - itemAmount;
        _balances[msg.sender][id] = _balances[msg.sender][id] + itemAmount;
        
        return true;
    }
"""
        elif primary_erc == "erc721" and secondary_erc == "erc1155":
            return """
    /// @notice Generic ERC721-ERC1155 interaction
    /// @notice postcondition _tokenOwner[tokenId] == itemOwner || !success
    /// @notice postcondition _ownedTokensCount[msg.sender] == __verifier_old_uint(_ownedTokensCount[msg.sender]) - 1 || !success
    /// @notice postcondition _ownedTokensCount[itemOwner] == __verifier_old_uint(_ownedTokensCount[itemOwner]) + 1 || !success
    /// @notice postcondition _balances[itemOwner][id] == __verifier_old_uint(_balances[itemOwner][id]) - itemAmount || !success
    /// @notice postcondition _balances[msg.sender][id] == __verifier_old_uint(_balances[msg.sender][id]) + itemAmount || !success
    function swapNFTForMultiItems(uint256 tokenId, address itemOwner, uint256 id, uint256 itemAmount) public returns (bool success) {
        require(_tokenOwner[tokenId] == msg.sender, "ERC721: not token owner");
        require(_balances[itemOwner][id] >= itemAmount, "ERC1155: insufficient balance");
        
        // Transfer NFT
        _tokenOwner[tokenId] = itemOwner;
        _ownedTokensCount[msg.sender] = _ownedTokensCount[msg.sender] - 1;
        _ownedTokensCount[itemOwner] = _ownedTokensCount[itemOwner] + 1;
        
        // Transfer multi-items
        _balances[itemOwner][id] = _balances[itemOwner][id] - itemAmount;
        _balances[msg.sender][id] = _balances[msg.sender][id] + itemAmount;
        
        return true;
    }
"""
        else:
            return """
    /// @notice Generic cross-ERC interaction
    /// @notice postcondition true
    function crossInteraction() public returns (bool success) {
        // Generic interaction between standards
        return true;
    }
"""

    def _create_cross_contract(self, primary_erc: str, secondary_erc: str, interaction_code: str, pattern_name: str) -> str:
        """Create a contract that combines two ERC standards with the interaction code"""
        # We'll create a simple hybrid contract that references state variables from both standards
        primary_erc_name = primary_erc.upper()
        secondary_erc_name = secondary_erc.upper()
        
        # State variables from ERC20
        erc20_state = """
    // ERC20 state variables
    mapping (address => uint256) private _balances;
    mapping (address => mapping (address => uint256)) private _allowed;
    uint256 private _totalSupply;
"""

        # State variables from ERC721
        erc721_state = """
    // ERC721 state variables
    mapping (uint256 => address) private _tokenOwner;
    mapping (address => uint256) private _ownedTokensCount;
    mapping (uint256 => address) private _tokenApprovals;
    mapping (address => mapping (address => bool)) private _operatorApprovals;
"""

        # State variables from ERC1155
        erc1155_state = """
    // ERC1155 state variables
    mapping (address => mapping(uint256 => uint256)) private _balances;
    mapping (address => mapping (address => bool)) private _operatorApprovals;
"""

        # Additional state for cross-interaction
        additional_state = {
            "token_purchase": """
    // Token purchase state
    mapping (uint256 => uint256) private _tokenPrices;
""",
            "staking": """
    // Staking state
    mapping (address => uint256) private stakedAmount;
    mapping (address => uint256) private lastStakeTime;
    uint256 private nextTokenId = 1;
""",
            "nft_bundling": """
    // Bundle state
    struct Bundle {
        address owner;
        uint256 tokenId;
        uint256 itemId;
        uint256 itemAmount;
    }
    mapping (uint256 => Bundle) private bundles;
    uint256 private nextBundleId = 1;
"""
        }
        
        # Combine state variables based on the ERCs involved
        state_variables = ""
        if "erc20" in [primary_erc, secondary_erc]:
            state_variables += erc20_state
        if "erc721" in [primary_erc, secondary_erc]:
            state_variables += erc721_state
        if "erc1155" in [primary_erc, secondary_erc]:
            state_variables += erc1155_state
        
        # Add additional state if available for the pattern
        if pattern_name in additional_state:
            state_variables += additional_state[pattern_name]
        
        # Helper functions needed for the interaction
        helper_functions = {
            "staking": """
    function _getNextTokenId() private returns (uint256) {
        return nextTokenId++;
    }
"""
        }
        
        # Add helper functions if available for the pattern
        helper_code = ""
        if pattern_name in helper_functions:
            helper_code = helper_functions[pattern_name]
        
        # Create the contract
        contract = f"""pragma solidity >=0.5.0;

/**
 * @title {primary_erc_name}{secondary_erc_name}Hybrid
 * @dev A hybrid contract implementing both {primary_erc_name} and {secondary_erc_name} standards with cross-interaction.
 */
contract {primary_erc_name}{secondary_erc_name}Hybrid {{
{state_variables}
    
    // Events from both standards
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);
    
    // Cross-ERC interaction: {pattern_name}
{interaction_code}
{helper_code}
}}
"""
        return contract 