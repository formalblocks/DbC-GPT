/// @notice postcondition (  __verifier_old_uint(_balances[msg.sender]) == _balances[msg.sender] + _amount && msg.sender != _recipient  )
/// @notice postcondition ( _balances[_recipient] == __verifier_old_uint(_balances[_recipient]) + _amount && msg.sender != _recipient )
/// @notice emits Transfer
function transfer(address _recipient, uint256 _amount) public returns (bool success);