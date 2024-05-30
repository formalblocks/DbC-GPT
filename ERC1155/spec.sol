// SPDX-License-Identifier: MIT
pragma solidity >= 0.5.0;

contract IERC1155  {

    /// @notice postcondition _balances[id][_owner] == balance 
    function balanceOf(address _owner, uint256 id) external view returns (uint256);

    /// @notice postcondition batchBalances.length == _owners.length
    /// @notice postcondition batchBalances.length == ids.length
    /// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[ids[x]][_owners[x]] 
    function balanceOfBatch(address[] calldata _owners, uint256[] calldata ids) external view returns (uint256[] memory batchBalances);

    /// @notice  postcondition operators[msg.sender][_operator] ==  _approved\n/// @notice  emits  ApprovalForAll
    function setApprovalForAll(address _operator, bool _approved) external;

    /// @notice postcondition operators[_owner][_operator] == isOperator 
    function isApprovedForAll(address _owner, address _operator) external view returns (bool);
    
    /// @notice postcondition _to != address(0)\n/// @notice postcondition operators[_from][msg.sender] || _from == msg.sender\n/// @notice postcondition __verifier_old_uint ( balances[_from][_id] ) >= _value\n/// @notice postcondition balances[_from][_id] == __verifier_old_uint ( balances[_from][_id] ) - _value\n/// @notice postcondition balances[_to][_id] == __verifier_old_uint ( balances[_to][_id] ) + _value
    function safeTransferFrom(address _from, address _to, uint256 id, uint256 _value, bytes calldata _data) external;

    /// @notice postcondition _to != address(0)\n/// @notice postcondition operators[_from][msg.sender] || _from == msg.sender 
    function safeBatchTransferFrom(address _from, address _to, uint256[] calldata _ids, uint256[] calldata _values, bytes calldata _data) external;
}
