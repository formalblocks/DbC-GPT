mapping (address => uint256) private _balances;

mapping (address => mapping (address => uint256)) private _allowed;

uint256 private _totalSupply;

#### approve

Allows `_spender` to withdraw from your account multiple times, up to the `_value` amount. If this function is called again it overwrites the current allowance with `_value`.

To prevent attack vectors, clients SHOULD make sure to create user interfaces in such a way that they set the allowance first to `0` before setting it to another value for the same spender.
THOUGH The contract itself shouldn't enforce it, to allow backwards compatibility with contracts deployed before

$ADD POSTCONDITION HERE
function approve(address _spender, uint256 _value) public returns (bool success)