/// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
/// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _ownedTokensCount[_to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
/// @notice  postcondition  _tokenOwner[_tokenId] == _to
function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes calldata _data) external;