pragma solidity >=0.5.0 <0.9.0;

/**
 * @title ERC721 Non-Fungible Token Standard basic interface
 * @dev see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-721.md
 */
contract IERC721 {

    bytes4 private constant _ERC721_RECEIVED = 0x150b7a02;

    mapping (uint256 => address) private _tokenOwner;

    mapping (uint256 => address) private _tokenApprovals;

    mapping (address => uint256) private _ownedTokensCount;

    mapping (address => mapping (address => bool)) private _operatorApprovals;

    bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;
    
    function balanceOf(address owner) external view returns (uint256 balance);

    function ownerOf(uint256 tokenId) external view returns (address _owner);
    
    function approve(address to, uint256 tokenId) external;
    
    function getApproved(uint256 tokenId) external view returns (address approved);

    function setApprovalForAll(address to, bool approved) external;

    function isApprovedForAll(address owner, address operator) external view returns (bool);

    function transferFrom(address from, address to, uint256 tokenId) external;
    
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata _data) external;
}