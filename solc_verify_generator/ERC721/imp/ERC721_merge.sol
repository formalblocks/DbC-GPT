
contract Refinement {

    struct StateOld {
        mapping (uint256 => address) _tokenOwner;
        mapping (uint256 => address) _tokenApprovals;
        mapping (address => uint256) _ownedTokensCount;
        mapping (address => mapping (address => bool)) _operatorApprovals;
    }

    struct StateNew {
        mapping (uint256 => address) _tokenOwner;
        mapping (uint256 => address) _tokenApprovals;
        mapping (address => uint256) _ownedTokensCount;
        mapping (address => mapping (address => bool)) _operatorApprovals;
    }

    StateOld abs;
    StateOld abs_old;
    StateNew con;
    StateNew con_old;

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address _owner, uint256 balance) public view returns (uint256) {}

    ///@notice postcondition _owner != address(0)
///@notice postcondition balance == con._ownedTokensCount[_owner]

    function balanceOf_post(address _owner, uint256 balance) public view returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function ownerOf_pre(uint256 _tokenId, address _owner) public view returns (address) {}

    ///@notice postcondition _owner != address(0)
///@notice postcondition _owner == con._tokenOwner[_tokenId]

    function ownerOf_post(uint256 _tokenId, address _owner) public view returns (address) {}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address _approved, uint256 _tokenId) public {}

    ///@notice postcondition con._tokenApprovals[_tokenId] == _approved
///@notice postcondition _approved == address(0) || con._tokenApprovals[_tokenId] != address(0)

    function approve_post(address _approved, uint256 _tokenId) public;

    /// @notice precondition true
    /// @notice postcondition true
    function getApproved_pre(uint256 _tokenId, address approved) public view returns (address) {}

    ///@notice postcondition approved == con._tokenApprovals[_tokenId]

    function getApproved_post(uint256 _tokenId, address approved) public view returns (address) {}

    /// @notice precondition true
    /// @notice postcondition true
    function setApprovalForAll_pre(address _operator, bool _approved) public {}

    ///@notice postcondition con._operatorApprovals[msg.sender][_operator] == _approved

    function setApprovalForAll_post(address _operator, bool _approved) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function isApprovedForAll_pre(address _owner, address _operator, bool approved) public view returns (bool) {}

    ///@notice postcondition approved == con._operatorApprovals[_owner][_operator]

    function isApprovedForAll_post(address _owner, address _operator, bool approved) public view returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transferFrom_pre(address _from, address _to, uint256 _tokenId) public {}

    ///@notice postcondition con._tokenOwner[_tokenId] == _to
///@notice postcondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice postcondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice postcondition con._tokenApprovals[_tokenId] == address(0)

    function transferFrom_post(address _from, address _to, uint256 _tokenId) public {}


    ///@notice postcondition con._tokenOwner[_tokenId] == _to
///@notice postcondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice postcondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice postcondition con._tokenApprovals[_tokenId] == address(0)

    function safeTransferFrom_post(address _from, address _to, uint256 _tokenId) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeTransferFrom_pre(address _from, address _to, uint256 _tokenId, bytes memory data) public {}

    ///@notice postcondition con._tokenOwner[_tokenId] == _to
///@notice postcondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice postcondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice postcondition con._tokenApprovals[_tokenId] == address(0)

    function safeTransferFrom_post(address _from, address _to, uint256 _tokenId, bytes memory data) public {}
}
