// SPDX-License-Identifier: MIT
pragma solidity >=0.5.7;

/// @notice  invariant  _totalSupply  ==  __verifier_sum_uint(_balances)
contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed _from, address indexed _to, uint _value);
    event Approval(address indexed _owner, address indexed _spender, uint _value);

    /**
     * @dev Returns the value of tokens in existence.
     */
    function totalSupply() external view returns (uint256);

    /**
     * @dev Returns the value of tokens owned by `_owner`.
    */
    function balanceOf(address _owner) public view returns (uint256 balance);

    /**
     * @dev Moves a `_value` amount of tokens from the caller's account to `_to`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transfer(address _to, uint256 _value) public returns (bool success);

    /**
     * @dev Returns the remaining number of tokens that `_spender` will be
     * allowed to spend on behalf of `_owner` through {transferFrom}. This is
     * zero by default.
     *
     * This value changes when {approve} or {transferFrom} are called.
     */
    function allowance(address _owner, address _spender) public view returns (uint256 remaining);

    /**
     * @dev Sets a `_value` amount of tokens as the allowance of `_spender` over the
     * caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits an {Approval} event.
     */
    function approve(address _spender, uint256 _value) public returns (bool success);

    /**
     * @dev Moves a `_value` amount of tokens from `_from` to `_to` using the
     * allowance mechanism. `_value` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);
}