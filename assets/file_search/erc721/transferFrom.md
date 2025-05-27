// Mapping from token ID to owner
mapping (uint256 => address) private _tokenOwner;

// Mapping from token ID to approved address
mapping (uint256 => address) private _tokenApprovals;

// Mapping from owner to number of owned token
mapping (address => uint256) private _ownedTokensCount;

// Mapping from owner to operator approvals
mapping (address => mapping (address => bool)) private _operatorApprovals;

/// @notice Transfer ownership of an NFT -- THE CALLER IS RESPONSIBLE
/// TO CONFIRM THAT `_to` IS CAPABLE OF RECEIVING NFTS OR ELSE
/// THEY MAY BE PERMANENTLY LOST
/// @dev Throws unless `msg.sender` is the current owner, an authorized
/// operator, or the approved address for this NFT. Throws if `_from` is
/// not the current owner. Throws if `_to` is the zero address. Throws if
/// `_tokenId` is not a valid NFT.
/// @param _from The current owner of the NFT
/// @param _to The new owner
/// @param _tokenId The NFT to transfer

$ADD POSTCONDITION HERE
function transferFrom(address _from, address _to, uint256 _tokenId) external payable;