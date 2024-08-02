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

    /// @notice precondition forall (address _owner, uint256 _id) abs._balances[_id][_owner] == con._balances[_id][_owner] // Abs func
    /// @notice precondition abs._balances[_id][_owner] == balance
    ///@notice postcondition con._balances[_id][_owner] == balance

    function balanceOf_post(address _owner, uint256 _id, uint256 balance) public view returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOfBatch_pre(address[] memory _owners, uint256[] memory _ids, uint256[] memory batchBalances) public view returns (uint256[] memory) {}

    /// @notice precondition forall (uint x) abs._balances[_ids[x]][_owners[x]] == con._balances[_ids[x]][_owners[x]] // Abs func
    /// @notice precondition batchBalances.length == _owners.length
    /// @notice precondition batchBalances.length == _ids.length
    /// @notice precondition forall (uint x) !(0 <= x && x < _owners.length) || abs._balances[_ids[x]][_owners[x]] == batchBalances[x]
    ///@notice postcondition batchBalances.length == _owners.length 
/// @notice postcondition batchBalances.length == _ids.length
/// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == con._balances[_ids[x]][_owners[x]]

    function balanceOfBatch_post(address[] memory _owners, uint256[] memory _ids, uint256[] memory batchBalances) public view returns (uint256[] memory) {}

    /// @notice precondition true
    /// @notice postcondition true
    function setApprovalForAll_pre(address _operator, bool _approved) public {}

    /// @notice precondition forall (address owner, address operator) abs._operatorApprovals[owner][operator] == con._operatorApprovals[owner][operator] // Abs func
    /// @notice precondition abs._operatorApprovals[msg.sender][_operator] == _approved
    ///@notice postcondition con._operatorApprovals[msg.sender][_operator] ==  _approved 

    function setApprovalForAll_post(address _operator, bool _approved) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function isApprovedForAll_pre(address _owner, address _operator, bool approved) public view returns (bool) {}

    /// @notice precondition forall (address _owner, address _operator) abs._operatorApprovals[_owner][_operator] == con._operatorApprovals[_owner][_operator] // Abs func
    /// @notice precondition abs._operatorApprovals[_owner][_operator] == approved
    ///@notice postcondition con._operatorApprovals[_owner][_operator] == approved

    function isApprovedForAll_post(address _owner, address _operator, bool approved) public view returns (bool) {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeTransferFrom_pre(address _from, address _to, uint256 _id, uint256 _value) public {}

    /// @notice precondition forall (uint256 _id, address _from) abs._balances[_id][_from] == con._balances[_id][_from] // Abs func
    /// @notice precondition forall (uint256 _id, address _from) abs_old._balances[_id][_from] == con_old._balances[_id][_from] // Abs func
    /// @notice precondition forall (uint256 _id, address _to) abs._balances[_id][_to] == con._balances[_id][_to] // Abs func
    /// @notice precondition forall (uint256 _id, address _to) abs_old._balances[_id][_to] == con_old._balances[_id][_to] // Abs func
    /// @notice precondition forall (address _from) abs._operatorApprovals[_from][msg.sender] == con._operatorApprovals[_from][msg.sender]
    /// @notice precondition _to != address(0)
    /// @notice precondition abs._operatorApprovals[_from][msg.sender] || _from == msg.sender
    /// @notice precondition abs_old._balances[_id][_from] >= _value    
    /// @notice precondition abs._balances[_id][_from] == abs_old._balances[_id][_from] - _value
    /// @notice precondition abs._balances[_id][_to] == abs_old._balances[_id][_to] + _value
    ///@notice postcondition _to != address(0) 
/// @notice postcondition con._operatorApprovals[_from][msg.sender] || _from == msg.sender
/// @notice postcondition con_old._balances[_id][_from] >= _value    
/// @notice postcondition con._balances[_id][_from] == con_old._balances[_id][_from] - _value
/// @notice postcondition con._balances[_id][_to] == con_old._balances[_id][_to] + _value

    function safeTransferFrom_post(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public {}

    /// @notice precondition true
    /// @notice postcondition true
    function safeBatchTransferFrom_pre(address _from, address _to, uint256[] memory _ids, uint256[] memory _values) public {}

    /// @notice precondition forall (uint i, address _from) abs._balances[_ids[i]][_to] == con._balances[_ids[i]][_to] // Abs func
    /// @notice precondition forall (uint i, address _from) abs_old._balances[_ids[i]][_to] == con_old._balances[_ids[i]][_to] // Abs func
    /// @notice precondition forall (uint i, address _to) abs._balances[_ids[i]][_from] == con._balances[_ids[i]][_from] // Abs func
    /// @notice precondition forall (uint i, address _to) abs_old._balances[_ids[i]][_from] == con_old._balances[_ids[i]][_from] // Abs func

    /// @notice precondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (abs._balances[_ids[i]][_to] == abs_old._balances[_ids[i]][_to] + _values[i])
    /// @notice precondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (abs._balances[_ids[i]][_from] == abs_old._balances[_ids[i]][_from] - _values[i])
    ///@notice postcondition _to != address(0)
/// @notice postcondition con._operatorApprovals[_from][msg.sender] || _from == msg.sender
/// @notice postcondition _ids.length == _values.length
/// @notice postcondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (con._balances[_ids[i]][_to] == con_old._balances[_ids[i]][_to] + _values[i])

    function safeBatchTransferFrom_post(address _from, address _to, uint256[] memory _ids, uint256[] memory _values, bytes memory _data) public {}
}
