mapping (address => uint256) private _balances;

mapping (address => mapping (address => uint256)) private _allowed;

uint256 private _totalSupply;

#### allowance

Returns the amount which `_spender` is still allowed to withdraw from `_owner`.

$ADD POSTCONDITION HERE
function allowance(address _owner, address _spender) public view returns (uint256 remaining)