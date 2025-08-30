mapping (address => uint256) private _balances;

mapping (address => mapping (address => uint256)) private _allowed;

uint256 private _totalSupply;

#### totalSupply

Returns the total token supply.

$ADD POSTCONDITION HERE
function totalSupply() public view returns (uint256 supply);