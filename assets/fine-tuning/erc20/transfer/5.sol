/// @notice postcondition (  __verifier_old_uint(_balances[msg.sender]) - _tokens == _balances[msg.sender] && msg.sender != receiver  )
/// @notice postcondition ( _balances[receiver] == __verifier_old_uint(_balances[receiver]) + _tokens && msg.sender != receiver )
/// @notice emits Transfer
function transfer(address receiver, uint256 _tokens) public returns (bool success);