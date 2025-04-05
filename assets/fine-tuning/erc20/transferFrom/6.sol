/// @notice postcondition ( _balances[_from] == __verifier_old_uint(_balances[_from]) - _value && _from != _to ) || (_balances[_from] == __verifier_old_uint(_balances[_from]) && _from == _to)
/// @notice postcondition ( _balances[_to] == __verifier_old_uint(_balances[_to]) + _value && _from != _to ) || (_balances[_to] == __verifier_old_uint(_balances[_to]) && _from == _to)
/// @notice postcondition _allowed[_from][msg.sender] == __verifier_old_uint(_allowed[_from][msg.sender]) - _value
function transferFrom(address _from, address _to, uint256 _value) public returns (bool success); 