/// @notice postcondition (_balances[h] == __verifier_old_uint(_balances[h]) || ( __verifier_old_uint(_balances[h] ==  _balances[h] ) - t && h != r ) && h == r)
/// @notice postcondition ( _balances[r] == __verifier_old_uint(_balances[r]) + t && h != r ) || (_balances[r] == __verifier_old_uint(_balances[r]) && h == r)
/// @notice postcondition __verifier_old_uint(_allowed[h][msg.sender]) - t == _allowed[h][msg.sender] 
function transferFrom(address h, address r, uint256 t) public returns (bool success);