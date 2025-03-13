contract IERC1155  {

     /// @notice postcondition _balances[id][account] == balance  
    function balanceOf(address account, uint256 id) public view   returns (uint256 balance);

    
    /// @notice postcondition batchBalances.length == accounts.length 
    /// @notice postcondition batchBalances.length == ids.length
    /// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[ids[x]][accounts[x]]  
    function balanceOfBatch(
        address[] memory accounts,
        uint256[] memory ids
    )
        public
        view
        returns (uint256[] memory batchBalances);

    
    /// @notice  postcondition _operatorApprovals[msg.sender][operator] ==  approved 
    /// @notice  emits  ApprovalForAll 
    function setApprovalForAll(address operator, bool approved) public;

    /// @notice postcondition _operatorApprovals[account][operator] == approved 
    function isApprovedForAll(address account, address operator) public view   returns (bool approved);

    /// @notice precondition from != msg.sender
    /// @notice precondition !_operatorApprovals[from][msg.sender]
    /// @notice postcondition to != address(0) 
    /// @notice postcondition _operatorApprovals[from][msg.sender] || from == msg.sender
    /// @notice postcondition __verifier_old_uint ( _balances[id][from] ) >= amount    
    /// @notice postcondition _balances[id][from] == __verifier_old_uint ( _balances[id][from] ) - amount
    /// @notice postcondition _balances[id][to] == __verifier_old_uint ( _balances[id][to] ) + amount
    /// @notice emits TransferSingle 
    function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    )
        public;


    /// @notice postcondition _operatorApprovals[from][msg.sender] || from == msg.sender
    /// @notice postcondition to != address(0)
    /// @notice emits TransferBatch  
    function safeBatchTransferFrom(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    )
        public;

}
