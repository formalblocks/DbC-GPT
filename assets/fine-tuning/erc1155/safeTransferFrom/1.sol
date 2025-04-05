/// @notice postcondition _to != address(0) 
/// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
/// @notice postcondition __verifier_old_uint ( _balances[_id][_from] ) >= _value    
/// @notice postcondition _balances[_id][_from] == __verifier_old_uint ( _balances[_id][_from] ) - _value
/// @notice postcondition _balances[_id][_to] == __verifier_old_uint ( _balances[_id][_to] ) + _value
function safeTransferFrom(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public;