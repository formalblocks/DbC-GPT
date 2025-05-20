// Mapping from token ID to account balances
mapping (uint256 => mapping(address => uint256)) private _balances;

// Mapping from account to operator approvals
mapping (address => mapping(address => bool)) private _operatorApprovals;

/**
    @notice Get the balance of an account's tokens.
    @param _owner  The address of the token holder
    @param _id     ID of the token
    @return        The _owner's balance of the token type requested
*/
$ADD POSTCONDITION HERE
function balanceOf(address _owner, uint256 _id) public view   returns (uint256 balance);
