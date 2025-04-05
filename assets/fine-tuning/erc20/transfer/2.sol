/// @notice postcondition ( _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - val && msg.sender != t )
/// @notice postcondition ( _balances[t] == __verifier_old_uint(_balances[t]) + val && msg.sender != t )
function transfer(address t, uint256 val) public returns (bool s);