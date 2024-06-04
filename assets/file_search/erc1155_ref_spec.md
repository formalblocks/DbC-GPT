// SPDX-License-Identifier: MIT

pragma solidity >= 0.5.0;

contract IERC1155  {
    /// @notice postcondition _balances[_id][_owner] == balance  
    function balanceOf(address _owner, uint256 _id) public view   returns (uint256 balance);
    
    /// @notice postcondition batchBalances.length == _owners.length 
    /// @notice postcondition batchBalances.length == _ids.length
    /// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[_ids[x]][_owners[x]]
    function balanceOfBatch(address[] memory _owners, uint256[] memory _ids) public view returns (uint256[] memory batchBalances);

    /// @notice  postcondition _operatorApprovals[msg.sender][_operator] ==  _approved 
    /// @notice  emits  ApprovalForAll
    function setApprovalForAll(address _operator, bool _approved) public;

    /// @notice postcondition _operatorApprovals[_owner][_operator] == approved
    function isApprovedForAll(address _owner, address _operator) public view   returns (bool approved);

    /// @notice precondition _from != msg.sender
    /// @notice precondition !_operatorApprovals[_from][msg.sender]
    /// @notice postcondition _to != address(0) 
    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
    /// @notice postcondition __verifier_old_uint ( _balances[_id][_from] ) >= _value    
    /// @notice postcondition _balances[_id][_from] == __verifier_old_uint ( _balances[_id][_from] ) - _value
    /// @notice postcondition _balances[_id][_to] == __verifier_old_uint ( _balances[_id][_to] ) + _value
    /// @notice emits TransferSingle
    function safeTransferFrom(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public;

    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
    /// @notice postcondition _to != address(0)
    /// @notice emits TransferBatch
    function safeBatchTransferFrom(address _from, address _to, uint256[] memory _ids, uint256[] memory _values, bytes memory _data) public;
}