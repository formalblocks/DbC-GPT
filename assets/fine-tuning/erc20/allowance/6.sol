/// @notice postcondition fundsAvailable == _allowed[_holder][_authorizedUser]
function allowance(address _holder, address _authorizedUser) public view returns (uint256 fundsAvailable);