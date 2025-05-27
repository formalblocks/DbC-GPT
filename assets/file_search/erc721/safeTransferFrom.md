// Mapping from token ID to owner
mapping (uint256 => address) private _tokenOwner;

// Mapping from token ID to approved address
mapping (uint256 => address) private _tokenApprovals;

// Mapping from owner to number of owned token
mapping (address => uint256) private _ownedTokensCount;

// Mapping from owner to operator approvals
mapping (address => mapping (address => bool)) private _operatorApprovals;

/// @notice Transfers the ownership of an NFT from one address to another address
/// @dev This works identically to the other function with an extra data parameter,
/// except this function just sets data to "".
/// @param _from The current owner of the NFT
/// @param _to The new owner
/// @param _tokenId The NFT to transfer

$ADD POSTCONDITION HERE
function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable;