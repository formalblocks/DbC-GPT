contract Refinement {

    struct StateOld {
        mapping (uint256 => mapping(address => uint256)) _balances;
        mapping (address => mapping(address => bool)) _operatorApprovals;
    }

    struct StateNew {
        mapping (uint256 => mapping(address => uint256)) _balances;
        mapping (address => mapping(address => bool)) _operatorApprovals;
    }

    StateOld abs;
    StateOld abs_old;
    StateNew con;
    StateNew con_old;

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address _owner, uint256 _id, uint256 balance) public view returns (uint256) {}

    ///@notice postcondition con._balances[_id][_owner] == balance

    function balanceOf_post(address _owner, uint256 _id, uint256 balance) public view returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOfBatch_pre(address[] memory _owners, uint256[] memory _ids, uint256[] memory batchBalances) public view returns (uint256[] memory) {}

    ///@notice postcondition batchBalances.length == _owners.length 
/// @notice postcondition batchBalances.length == _ids.length
/// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == con._balances[_ids[x]][_owners[x]]

    function balanceOfBatch_post(address[] memory _owners, uint256[] memory _ids, uint256[] memory batchBalances) public view returns (uint256[] memory) {}

    /// @notice precondition true
    /// @notice postcondition true
    function setApprovalForAll_pre(address _operator, bool _approved) public {}

    ///@notice postcondition con._operatorApprovals[msg.sender][_operator] == _approved

    function setApprovalForAll_post(address _operator, bool _approved) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function isApprovedForAll_pre(address _owner, address _operator, bool approved) public view returns (bool) {}

    ///@notice postcondition con._operatorApprovals[_owner][_operator] == approved

    function isApprovedForAll_post(address _owner, address _operator, bool approved) public view returns (bool) {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeTransferFrom_pre(address _from, address _to, uint256 _id, uint256 _value) public {}

    ///@notice postcondition _to != address(0)
/// @notice postcondition con._operatorApprovals[_from][msg.sender] || _from == msg.sender
/// @notice postcondition con_old._balances[_id][_from] >= _value    
/// @notice postcondition con._balances[_id][_from] == con_old._balances[_id][_from] - _value
/// @notice postcondition con._balances[_id][_to] == con_old._balances[_id][_to] + _value

    function safeTransferFrom_post(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeBatchTransferFrom_pre(address _from, address _to, uint256[] memory _ids, uint256[] memory _values) public {}

    ///@notice postcondition _to != address(0)
/// @notice postcondition _ids.length == _values.length
/// @notice postcondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (con._balances[_ids[i]][_to] == con_old._balances[_ids[i]][_to] + _values[i])
/// @notice postcondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (con._balances[_ids[i]][_from] == con_old._balances[_ids[i]][_from] - _values[i])

    function safeBatchTransferFrom_post(address _from, address _to, uint256[] memory _ids, uint256[] memory _values, bytes memory _data) public {}
}
