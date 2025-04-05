/// @notice postcondition remainingBalance == _allowed[_owner][_approvedAddress]
function allowance(address _owner, address _approvedAddress) public view returns (uint256 remainingBalance);