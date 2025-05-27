// Mapping from token ID to owner
mapping (uint256 => address) private _tokenOwner;

// Mapping from token ID to approved address
mapping (uint256 => address) private _tokenApprovals;

// Mapping from owner to number of owned token
mapping (address => uint256) private _ownedTokensCount;

// Mapping from owner to operator approvals
mapping (address => mapping (address => bool)) private _operatorApprovals;

/// @notice Change or reaffirm the approved address for an NFT
/// @dev The zero address indicates there is no approved address.
/// Throws unless `msg.sender` is the current NFT owner, or an authorized
/// operator of the current owner.
/// @param _approved The new approved NFT controller
/// @param _tokenId The NFT to approve

$ADD POSTCONDITION HERE
function approve(address _approved, uint256 _tokenId) external payable;
