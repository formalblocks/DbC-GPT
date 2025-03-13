```solidity
pragma solidity >=0.5.0;

contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    /**
    * Returns the total token supply.
    */
    $ADD POSTCONDITION HERE
    function totalSupply() public view returns (uint256 supply);

    /**
    * Transfers `_value` amount of tokens to address `_to`, and MUST fire the `Transfer` event.
    * The function SHOULD `throw` if the message caller's account balance does not have enough tokens to spend.

    * *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.
    */
    $ADD POSTCONDITION HERE
    function transfer(address _to, uint256 _value) public returns (bool success);

    /**
    * Transfers `_value` amount of tokens from address `_from` to address `_to`, and MUST fire the `Transfer` event.
    * The `transferFrom` method is used for a withdraw workflow, allowing contracts to transfer tokens on your behalf.
    * This can be used for example to allow a contract to transfer tokens on your behalf and/or to charge fees in sub-currencies.
    * The function SHOULD `throw` unless the `_from` account has deliberately authorized the sender of the message via some mechanism.
    * *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.
    */
    $ADD POSTCONDITION HERE
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

    /**
    * Allows `_spender` to withdraw from your account multiple times, up to the `_value` amount. If this function is called again it overwrites the current allowance with `_value`.
    */
    $ADD POSTCONDITION HERE
    function approve(address _spender, uint256 _value) public returns (bool success);

    /**
    * Returns the account balance of another account with address `_owner`.
    */
    $ADD POSTCONDITION HERE
    function balanceOf(address _owner) public view returns (uint256 balance);

    /**
    * Returns the amount which `_spender` is still allowed to withdraw from `_owner`.
    */
    $ADD POSTCONDITION HERE
    function allowance(address _owner, address _spender) public view returns (uint256 remaining);
}
```
