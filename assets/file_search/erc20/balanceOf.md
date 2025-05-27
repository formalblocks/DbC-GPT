mapping (address => uint256) private _balances;

mapping (address => mapping (address => uint256)) private _allowed;

uint256 private _totalSupply;

#### balanceOf

Returns the account balance of another account with address `_owner`.

$ADD POSTCONDITION HERE
function balanceOf(address _owner) public view returns (uint256 balance)