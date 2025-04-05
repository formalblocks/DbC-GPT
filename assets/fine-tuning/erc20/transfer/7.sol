/// @notice postcondition (  __verifier_old_uint(_balances[msg.sender]) - _value == _balances[msg.sender] && msg.sender != ____target  )
/// @notice postcondition ( _balances[____target] == __verifier_old_uint(_balances[____target]) + _value && msg.sender != ____target )
/// @notice emits Transfer
function transfer(address ____target, uint256 _value) public returns (bool success);