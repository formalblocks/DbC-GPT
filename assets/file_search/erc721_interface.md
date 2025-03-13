```solidity
pragma solidity >=0.5.0;

contract IERC721 {

    bytes4 private constant _ERC721_RECEIVED = 0x150b7a02;

    mapping (uint256 => address) private _tokenOwner;

    mapping (uint256 => address) private _tokenApprovals;

    mapping (address => uint256) private _ownedTokensCount;

    mapping (address => mapping (address => bool)) private _operatorApprovals;

    bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;

    /**
        * @notice Count all NFTs assigned to an owner
        * @dev NFTs assigned to the zero address are considered invalid, and this
        *  function throws for queries about the zero address.
        * @param _owner An address for whom to query the balance
        * @return The number of NFTs owned by `_owner`, possibly zero
        */
    $ADD POSTCONDITION HERE
    function balanceOf(address _owner) external view returns (uint256 balance);

    /**
        * @notice Find the owner of an NFT
        * @dev NFTs assigned to zero address are considered invalid, and queries
        *  about them do throw.
        * @param _tokenId The identifier for an NFT
        * @return The address of the owner of the NFT
        */
    $ADD POSTCONDITION HERE
    function ownerOf(uint256 _tokenId) external view returns (address _owner);

    /**
        * @notice Change or reaffirm the approved address for an NFT
        * @dev The zero address indicates there is no approved address.
        *  Throws unless `msg.sender` is the current NFT owner, or an authorized
        *  operator of the current owner.
        * @param _approved The new approved NFT controller
        * @param _tokenId The NFT to approve
        */
    $ADD POSTCONDITION HERE
    function approve(address _approved, uint256 _tokenId) external;

    /**
        * @notice Get the approved address for a single NFT
        * @dev Throws if `_tokenId` is not a valid NFT.
        * @param _tokenId The NFT to find the approved address for
        * @return The approved address for this NFT, or the zero address if there is none
        */
    $ADD POSTCONDITION HERE
    function getApproved(uint256 _tokenId) external view returns (address approved);

    /**
        * @notice Enable or disable approval for a third party ("operator") to manage
        *  all of `msg.sender`'s assets
        * @dev Emits the ApprovalForAll event. The contract MUST allow
        *  multiple operators per owner.
        * @param _operator Address to add to the set of authorized operators
        * @param _approved True if the operator is approved, false to revoke approval
        */
    $ADD POSTCONDITION HERE
    function setApprovalForAll(address _operator, bool _approved) external;

    /**
        * @notice Query if an address is an authorized operator for another address
        * @param _owner The address that owns the NFTs
        * @param _operator The address that acts on behalf of the owner
        * @return True if `_operator` is an approved operator for `_owner`, false otherwise
        */
    $ADD POSTCONDITION HERE
    function isApprovedForAll(address _owner, address _operator) external view returns (bool);

    /**
        * @notice Transfer ownership of an NFT -- THE CALLER IS RESPONSIBLE
        *  TO CONFIRM THAT `_to` IS CAPABLE OF RECEIVING NFTS OR ELSE
        *  THEY MAY BE PERMANENTLY LOST
        * @dev Throws unless `msg.sender` is the current owner, an authorized
        *  operator, or the approved address for this NFT. Throws if `_from` is
        *  not the current owner. Throws if `_to` is the zero address. Throws if
        *  `_tokenId` is not a valid NFT.
        * @param _from The current owner of the NFT
        * @param _to The new owner
        * @param _tokenId The NFT to transfer
        */
    $ADD POSTCONDITION HERE
    function transferFrom(address _from, address _to, uint256 _tokenId) external;

    /**
        * @notice Transfers the ownership of an NFT from one address to another address
        * @dev This works identically to the other function with an extra data parameter,
        *  except this function just sets data to "".
        * @param _from The current owner of the NFT
        * @param _to The new owner
        * @param _tokenId The NFT to transfer
        */
    $ADD POSTCONDITION HERE
    function safeTransferFrom(address _from, address _to, uint256 _tokenId) external;

    /**
        * @notice Transfers the ownership of an NFT from one address to another address
        * @dev Throws unless `msg.sender` is the current owner, an authorized
        *  operator, or the approved address for this NFT. Throws if `_from` is
        *  not the current owner. Throws if `_to` is the zero address. Throws if
        *  `_tokenId` is not a valid NFT. When transfer is complete, this function
        *  checks if `_to` is a smart contract (code size > 0). If so, it calls
        *  `onERC721Received` on `_to` and throws if the return value is not
        *  `bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"))`.
        * @param _from The current owner of the NFT
        * @param _to The new owner
        * @param _tokenId The NFT to transfer
        * @param data Additional data with no specified format, sent in call to `_to`
        */
    $ADD POSTCONDITION HERE
    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes calldata _data) external;
}
```
