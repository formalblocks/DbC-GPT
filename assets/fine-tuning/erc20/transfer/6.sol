/// @notice postcondition (  __verifier_old_uint(_balances[msg.sender]) - _value == _balances[msg.sender] && msg.sender != beneficiary  )
/// @notice postcondition ( _balances[beneficiary] == __verifier_old_uint(_balances[beneficiary]) + _value && msg.sender != beneficiary )
/// @notice emits Transfer
function transfer(address beneficiary, uint256 _value) public returns (bool success);