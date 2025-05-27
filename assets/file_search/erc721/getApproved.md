// Mapping from token ID to owner
mapping (uint256 => address) private _tokenOwner;

// Mapping from token ID to approved address
mapping (uint256 => address) private _tokenApprovals;

// Mapping from owner to number of owned token
mapping (address => uint256) private _ownedTokensCount;

// Mapping from owner to operator approvals
mapping (address => mapping (address => bool)) private _operatorApprovals;

/// @notice Get the approved address for a single NFT
/// @dev Throws if `_tokenId` is not a valid NFT.
/// @param _tokenId The NFT to find the approved address for
/// @return The approved address for this NFT, or the zero address if there is none

$ADD POSTCONDITION HERE
function getApproved(uint256 _tokenId) external view returns (address);