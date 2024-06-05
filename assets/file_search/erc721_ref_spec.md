```solidity
pragma solidity >=0.5.0 <0.9.0;

/**
 * @title ERC721 Non-Fungible Token Standard basic interface
 * @dev see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md
 */
contract ERC721 {
    
    /// @notice postcondition _ownedTokensCount[_owner] == balance
    function balanceOf(address _owner) public view returns (uint256 balance);
    
    /// @notice postcondition _tokenOwner[_tokenId] == _owner
    /// @notice postcondition  _owner !=  address(0)
    function ownerOf(uint256 _tokenId) public view returns (address owner);

    /// @notice postcondition _tokenApprovals[_tokenId] == _approved 
    function approve(address _approved, uint256 _tokenId) external;
    
    /// @notice postcondition _tokenOwner[tokenId] != address(0)
    /// @notice postcondition _tokenApprovals[tokenId] == approved
    function getApproved(uint256 _tokenId) external view returns (address approved);

    /// @notice postcondition _operatorApprovals[msg.sender][_operator] == _approved
    function setApprovalForAll(address _operator, bool _approved) external;
    
    /// @notice postcondition _operatorApprovals[_owner][_operator] == approved
    function isApprovedForAll(address _owner, address _operator) external view returns (bool);

    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _owned_kensCount[to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice  postcondition  _tokenOwner[_tokenId] == _to
    function transferFrom(address _from, address _to, uint256 _tokenId) external;
    
    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _ownedTokensCount[_to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice  postcondition  _tokenOwner[_tokenId] == to
    function safeTransferFrom(address _from, address _to, uint256 _tokenId) external;

    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _ownedTokensCount[_to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice  postcondition  _tokenOwner[_tokenId] == _to
    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes calldata _data) external;
}
```