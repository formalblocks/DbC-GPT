// Mapping from token ID to owner
mapping (uint256 => address) private _tokenOwner;

// Mapping from token ID to approved address
mapping (uint256 => address) private _tokenApprovals;

// Mapping from owner to number of owned token
mapping (address => uint256) private _ownedTokensCount;

// Mapping from owner to operator approvals
mapping (address => mapping (address => bool)) private _operatorApprovals;

/// @notice Find the owner of an NFT
/// @dev NFTs assigned to zero address are considered invalid, and queries
/// about them do throw.
/// @param _tokenId The identifier for an NFT
/// @return The address of the owner of the NFT

$ADD POSTCONDITION HERE
function ownerOf(uint256 _tokenId) external view returns (address);