/// @notice postcondition _tokenOwner[_tokenId] == _owner
/// @notice postcondition  _owner !=  address(0)
function ownerOf(uint256 _tokenId) public view returns (address owner);