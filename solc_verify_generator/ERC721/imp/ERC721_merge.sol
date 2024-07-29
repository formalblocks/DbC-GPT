
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

    /// @notice precondition forall (address _owner) abs._ownedTokensCount[_owner] == con._ownedTokensCount[_owner] // Abs func
    ///@notice precondition _owner != address(0)
///@notice precondition balance == con._ownedTokensCount[_owner]

    /// @notice postcondition abs._ownedTokensCount[_owner] == balance
    function balanceOf_post(address _owner, uint256 balance) public view returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function ownerOf_pre(uint256 _tokenId, address _owner) public view returns (address) {}

    /// @notice precondition forall (uint256 _tokenId) abs._tokenOwner[_tokenId] == con._tokenOwner[_tokenId] // Abs func
    ///@notice precondition _owner != address(0)
///@notice precondition _owner == con._tokenOwner[_tokenId]

    /// @notice postcondition abs._tokenOwner[_tokenId] == _owner
    /// @notice postcondition  _owner !=  address(0)
    function ownerOf_post(uint256 _tokenId, address _owner) public view returns (address) {}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address _approved, uint256 _tokenId) public {}

    /// @notice precondition forall (uint256 _tokenId) abs._tokenApprovals[_tokenId] == con._tokenApprovals[_tokenId] // Abs func
    ///@notice precondition con._tokenApprovals[_tokenId] == _approved
///@notice precondition _approved == address(0) || con._tokenApprovals[_tokenId] != address(0)

    /// @notice postcondition abs._tokenApprovals[_tokenId] == _approved 
    function approve_post(address _approved, uint256 _tokenId) public;

    /// @notice precondition true
    /// @notice postcondition true
    function getApproved_pre(uint256 _tokenId, address approved) public view returns (address) {}

    /// @notice precondition forall (uint256 _tokenId) abs._tokenOwner[_tokenId] == con._tokenOwner[_tokenId] // Abs func
    /// @notice precondition forall (uint256 _tokenId) abs._tokenApprovals[_tokenId] == con._tokenApprovals[_tokenId] // Abs func
    ///@notice precondition approved == con._tokenApprovals[_tokenId]

    /// @notice postcondition abs._tokenOwner[_tokenId] != address(0)
    /// @notice postcondition abs._tokenApprovals[_tokenId] == approved
    function getApproved_post(uint256 _tokenId, address approved) public view returns (address) {}

    /// @notice precondition true
    /// @notice postcondition true
    function setApprovalForAll_pre(address _operator, bool _approved) public {}

    /// @notice precondition forall (address owner, address operator) abs._operatorApprovals[owner][operator] == con._operatorApprovals[owner][operator] // Abs func
    /// @notice precondition forall (address owner, address operator) abs_old._operatorApprovals[owner][operator] == con_old._operatorApprovals[owner][operator] // Abs func
    ///@notice precondition con._operatorApprovals[msg.sender][_operator] == _approved

    /// @notice postcondition abs._operatorApprovals[msg.sender][_operator] == _approved
    function setApprovalForAll_post(address _operator, bool _approved) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function isApprovedForAll_pre(address _owner, address _operator, bool approved) public view returns (bool) {}

    /// @notice precondition forall (address _owner, address _operator) abs._operatorApprovals[_owner][_operator] == con._operatorApprovals[_owner][_operator] // Abs func
    ///@notice precondition approved == con._operatorApprovals[_owner][_operator]

    /// @notice postcondition abs._operatorApprovals[_owner][_operator] == approved
    function isApprovedForAll_post(address _owner, address _operator, bool approved) public view returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transferFrom_pre(address _from, address _to, uint256 _tokenId) public {}

    /// @notice precondition forall (address _from) abs._ownedTokensCount[_from] == con._ownedTokensCount[_from] // Abs func
    /// @notice precondition forall (address _from) abs_old._ownedTokensCount[_from] == con_old._ownedTokensCount[_from] // Abs func
    /// @notice precondition forall (address _to) abs._ownedTokensCount[_to] == con._ownedTokensCount[_to] // Abs func
    /// @notice precondition forall (address _to) abs_old._ownedTokensCount[_to] == con_old._ownedTokensCount[_to] // Abs func
    /// @notice precondition forall (uint256 _tokenId) abs._tokenOwner[_tokenId] == con._tokenOwner[_tokenId] // Abs func
    ///@notice precondition con._tokenOwner[_tokenId] == _to
///@notice precondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice precondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice precondition con._tokenApprovals[_tokenId] == address(0)

    /// @notice postcondition ( ( abs._ownedTokensCount[_from] ==  abs_old._ownedTokensCount[_from] - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice postcondition ( ( abs._ownedTokensCount[_to] ==  abs_old._ownedTokensCount[_to] + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice postcondition  abs._tokenOwner[_tokenId] == _to
    function transferFrom_post(address _from, address _to, uint256 _tokenId) public {}


    /// @notice precondition forall (address _from) abs._ownedTokensCount[_from] == con._ownedTokensCount[_from] // Abs func
    /// @notice precondition forall (address _from) abs_old._ownedTokensCount[_from] == con_old._ownedTokensCount[_from] // Abs func
    /// @notice precondition forall (address _to) abs._ownedTokensCount[_to] == con._ownedTokensCount[_to] // Abs func
    /// @notice precondition forall (address _to) abs_old._ownedTokensCount[_to] == con_old._ownedTokensCount[_to] // Abs func
    /// @notice precondition forall (uint256 _tokenId) abs._tokenOwner[_tokenId] == con._tokenOwner[_tokenId] // Abs func
    ///@notice precondition con._tokenOwner[_tokenId] == _to
///@notice precondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice precondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice precondition con._tokenApprovals[_tokenId] == address(0)

    /// @notice postcondition ( ( abs._ownedTokensCount[_from] ==  abs_old._ownedTokensCount[_from] - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice postcondition ( ( abs._ownedTokensCount[_to] ==  abs_old._ownedTokensCount[_to] + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice postcondition  abs._tokenOwner[_tokenId] == _to
    function safeTransferFrom_post(address _from, address _to, uint256 _tokenId) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeTransferFrom_pre(address _from, address _to, uint256 _tokenId, bytes memory data) public {}

    /// @notice precondition forall (address _from) abs._ownedTokensCount[_from] ==  con._ownedTokensCount[_from] // Abs func
    /// @notice precondition forall (address _to) abs_old._ownedTokensCount[_to] ==  con_old._ownedTokensCount[_to] // Abs func
    /// @notice precondition forall (uint256 _tokenId) abs._tokenOwner[_tokenId] == con._tokenOwner[_tokenId] // Abs func
    ///@notice precondition con._tokenOwner[_tokenId] == _to
///@notice precondition con._ownedTokensCount[_from] == con._ownedTokensCount[_from] - 1 || con._ownedTokensCount[_from] == con._ownedTokensCount[_from]
///@notice precondition con._ownedTokensCount[_to] == con._ownedTokensCount[_to] || con._ownedTokensCount[_to] == con._ownedTokensCount[_to] + 1
///@notice precondition con._tokenApprovals[_tokenId] == address(0)

    /// @notice postcondition ( ( abs._ownedTokensCount[_from] ==  abs_old._ownedTokensCount[_from] - 1  &&  _from  != _to ) || ( _from == _to )  ) 
    /// @notice postcondition ( ( abs._ownedTokensCount[_to] ==  abs_old._ownedTokensCount[_to] + 1  &&  _from  != _to ) || ( _from  == _to ) )
    /// @notice postcondition  abs._tokenOwner[_tokenId] == _to
    function safeTransferFrom_post(address _from, address _to, uint256 _tokenId, bytes memory data) public {}
}
