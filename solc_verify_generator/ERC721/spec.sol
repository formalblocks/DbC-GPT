pragma solidity >=0.5.0 <0.9.0;

/**
 * @title ERC721 Non-Fungible Token Standard basic interface
 * @dev see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md
 */
contract IERC721 {
  

    /// @notice postcondition _ownedTokensCount[owner] == balance
    function balanceOf(address owner) public view returns (uint256 balance);
    /// @notice postcondition _tokenOwner[tokenId] == _owner
    /// @notice postcondition  _owner !=  address(0)
    function ownerOf(uint256 tokenId) public view returns (address owner);

    /// @notice postcondition _tokenApprovals[tokenId] == to 
    /// @notice emits Approval
    function approve(address to, uint256 tokenId) public;
    /// @notice postcondition _tokenOwner[tokenId] != address(0)
    /// @notice postcondition _tokenApprovals[tokenId] == approved
    function getApproved(uint256 tokenId) public view returns (address operator);

    /// @notice postcondition _operatorApprovals[msg.sender][to] == approved
    /// @notice emits ApprovalForAll
    function setApprovalForAll(address operator, bool _approved) public;
    /// @notice postcondition _operatorApprovals[owner][operator] == approved
    function isApprovedForAll(address owner, address operator) public view returns (bool);

    /// @notice  postcondition ( ( _ownedTokensCount[from] ==  __verifier_old_uint (_ownedTokensCount[from] ) - 1  &&  from  != to ) || ( from == to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[to] ==  __verifier_old_uint ( _ownedTokensCount[to] ) + 1  &&  from  != to ) || ( from  == to ) )
    /// @notice  postcondition  _tokenOwner[tokenId] == to
    /// @notice  emits Transfer
    function transferFrom(address from, address to, uint256 tokenId) public;
    /// @notice  postcondition ( ( _ownedTokensCount[from] ==  __verifier_old_uint (_ownedTokensCount[from] ) - 1  &&  from  != to ) || ( from == to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[to] ==  __verifier_old_uint ( _ownedTokensCount[to] ) + 1  &&  from  != to ) || ( from  == to ) )
    /// @notice  postcondition  _tokenOwner[tokenId] == to
    /// @notice  emits  Transfer
    function safeTransferFrom(address from, address to, uint256 tokenId) public;

    /// @notice  postcondition ( ( _ownedTokensCount[from] ==  __verifier_old_uint (_ownedTokensCount[from] ) - 1  &&  from  != to ) || ( from == to )  ) 
    /// @notice  postcondition ( ( _ownedTokensCount[to] ==  __verifier_old_uint ( _ownedTokensCount[to] ) + 1  &&  from  != to ) || ( from  == to ) )
    /// @notice  postcondition  _tokenOwner[tokenId] == to
    /// @notice  emits  Transfer
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory data) public;
}