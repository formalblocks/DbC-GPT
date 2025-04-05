/// @notice postcondition _tokenOwner[tokenId] != address(0)
/// @notice postcondition _tokenApprovals[tokenId] == approved
function getApproved(uint256 _tokenId) external view returns (address approved);