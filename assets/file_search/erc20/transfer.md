mapping (address => uint256) private _balances;

mapping (address => mapping (address => uint256)) private _allowed;

uint256 private _totalSupply;

#### transfer

Transfers `_value` amount of tokens to address `_to`, and MUST fire the `Transfer` event.
The function SHOULD `throw` if the message caller's account balance does not have enough tokens to spend.

*Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.

$ADD POSTCONDITION HERE
function transfer(address _to, uint256 _value) public returns (bool success)