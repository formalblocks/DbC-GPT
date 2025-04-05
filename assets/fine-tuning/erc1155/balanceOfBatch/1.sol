/// @notice postcondition batchBalances.length == _owners.length 
/// @notice postcondition batchBalances.length == _ids.length
/// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[_ids[x]][_owners[x]]
function balanceOfBatch(address[] memory _owners, uint256[] memory _ids) public view returns (uint256[] memory batchBalances);