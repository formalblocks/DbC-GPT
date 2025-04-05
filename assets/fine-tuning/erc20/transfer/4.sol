/// @notice postcondition (  __verifier_old_uint(_balances[msg.sender]) - _quantity == _balances[msg.sender] && msg.sender != _destination)
/// @notice postcondition ( _balances[_destination] == __verifier_old_uint(_balances[_destination]) + _quantity && msg.sender != _destination )
/// @notice emits Transfer
function transfer(address _destination, uint256 _quantity) public returns (bool success);