pragma solidity >=0.5.0 <0.9.0;

import "./IERC721Receiver.sol";
import "./SafeMath.sol";
import "./Address.sol";
import "./ERC165.sol";


contract ERC721 is ERC165 {
    using SafeMath for uint256;
    using Address for address;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    // Equals to `bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"))`
    // which can be also obtained as `IERC721Receiver(0).onERC721Received.selector`
    bytes4 private constant _ERC721_RECEIVED = 0x150b7a02;

    // Mapping from token ID to owner
    mapping (uint256 => address) private _tokenOwner;

    // Mapping from token ID to approved address
    mapping (uint256 => address) private _tokenApprovals;

    // Mapping from owner to number of owned token
    mapping (address => uint256) private _ownedTokensCount;

    // Mapping from owner to operator approvals
    mapping (address => mapping (address => bool)) private _operatorApprovals;

    bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;
    

    constructor () public {
        // register the supported interfaces to conform to ERC721 via ERC165
        _registerInterface(_INTERFACE_ID_ERC721);
    }

    ///@notice postcondition balance >= 0

    function balanceOf(address _owner) public view returns (uint256 balance) {
        require(_owner != address(0));
        return _ownedTokensCount[_owner];
    }

    ///@notice postcondition _tokenId == __verifier_old_uint(_tokenId)  && _owner == _tokenOwner[_tokenId]

    function ownerOf(uint256 _tokenId) public view returns (address _owner) {
        address owner = _tokenOwner[_tokenId];
        require(owner != address(0));
        return owner;
    }
   
    ///@notice postcondition _tokenApprovals[_tokenId] == _approved

    function approve(address _approved, uint256 _tokenId) public {
        address owner = ownerOf(_tokenId);
        require(_approved != owner);
        require(msg.sender == owner || isApprovedForAll(owner, msg.sender));

        _tokenApprovals[_tokenId] = _approved;
        emit Approval(owner, _approved, _tokenId);
    }


    ///@notice postcondition _tokenApprovals[_tokenId] == address(0) || approved == _tokenApprovals[_tokenId]

    function getApproved(uint256 _tokenId) public view returns (address approved) {
        require(_exists(_tokenId));
        return _tokenApprovals[_tokenId];
    }

    ///@notice postcondition (msg.sender == _owner && _operatorApprovals[msg.sender][_operator] == _approved) || (msg.sender != _owner && _operatorApprovals[msg.sender][_operator] == __verifier_old_bool(_approved))

    function setApprovalForAll(address _operator, bool _approved) public {
        require(_operator != msg.sender);
        _operatorApprovals[msg.sender][_operator] = _approved;
        emit ApprovalForAll(msg.sender, _operator, _approved);
    }

    ///@notice postcondition _owner == __verifier_old_address(_owner) 

    function isApprovedForAll(address _owner, address _operator) public view returns (bool approved) {
        return _operatorApprovals[_owner][_operator];
    }


    ///@notice postcondition _to != address(0)

    function transferFrom(address _from, address _to, uint256 _tokenId) public {
        require(_isApprovedOrOwner(msg.sender, _tokenId));
       
        _transferFrom(_from, _to, _tokenId);
    }

    ///@notice postcondition _to != address(0)

    function safeTransferFrom(address _from, address _to, uint256 _tokenId) public {
        safeTransferFrom(_from, _to, _tokenId, "");
    }

    ///@notice postcondition _to != address(0)

    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes memory _data) public {
        transferFrom(_from, _to, _tokenId);
        require(_checkOnERC721Received(_from, _to, _tokenId, _data));
    }

   
    function _exists(uint256 tokenId) internal view returns (bool) {
        address owner = _tokenOwner[tokenId];
        return owner != address(0);
    }

   
    function _isApprovedOrOwner(address spender, uint256 tokenId) internal view returns (bool) {
        address owner = ownerOf(tokenId);
        return (spender == owner || getApproved(tokenId) == spender || isApprovedForAll(owner, spender));
    }

    function _mint(address to, uint256 tokenId) internal {
        require(to != address(0));
        require(!_exists(tokenId));

        _tokenOwner[tokenId] = to;
        _ownedTokensCount[to] = _ownedTokensCount[to].add(1);

        emit Transfer(address(0), to, tokenId);
    }

    function _burn(address owner, uint256 tokenId) internal {
        require(ownerOf(tokenId) == owner);

        _clearApproval(tokenId);

        _ownedTokensCount[owner] = _ownedTokensCount[owner].sub(1);
        _tokenOwner[tokenId] = address(0);

        emit Transfer(owner, address(0), tokenId);
    }

    function _burn(uint256 tokenId) internal {
        _burn(ownerOf(tokenId), tokenId);
    }

   
    function _transferFrom(address from, address to, uint256 tokenId) internal {
        require(ownerOf(tokenId) == from);
        require(to != address(0));

        _clearApproval(tokenId);

        _ownedTokensCount[from] = _ownedTokensCount[from].sub(1);
        _ownedTokensCount[to] = _ownedTokensCount[to].add(1);

        _tokenOwner[tokenId] = to;

        emit Transfer(from, to, tokenId);
    }

    
    function _checkOnERC721Received(address from, address to, uint256 tokenId, bytes memory _data)
        internal returns (bool)
    {
        if (!to.isContract()) {
            return true;
        }

        bytes4 retval = IERC721Receiver(to).onERC721Received(msg.sender, from, tokenId, _data);
        return (retval == _ERC721_RECEIVED);
    }

    
    function _clearApproval(uint256 tokenId) private {
        if (_tokenApprovals[tokenId] != address(0)) {
            _tokenApprovals[tokenId] = address(0);
        }
    }
}