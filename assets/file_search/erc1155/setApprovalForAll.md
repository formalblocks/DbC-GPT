// Mapping from token ID to account balances
mapping (uint256 => mapping(address => uint256)) private _balances;

// Mapping from account to operator approvals
mapping (address => mapping(address => bool)) private _operatorApprovals;

/**
    @notice Enable or disable approval for a third party ("operator") to manage all of the caller's tokens.
    @dev MUST emit the ApprovalForAll event on success.
    @param _operator  Address to add to the set of authorized operators
    @param _approved  True if the operator is approved, false to revoke approval
*/

$ADD POSTCONDITION HERE
function setApprovalForAll(address _operator, bool _approved) public;