pragma solidity >=0.5.0;

contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);
   
    /// @notice Transfer `value` tokens to address `to`
    /// @param to Receiver of the tokens
    /// @param value Amount of tokens to transfer
    /// @return success True if transfer was successful
    function transfer(address to, uint value) public returns (bool success);

    /// @notice Transfer `value` tokens from address `from` to address `to`
    /// @param from Sender of tokens
    /// @param to Receiver of the tokens
    /// @param value Amount of tokens to be transferred
    /// @return success True if transfer was successful
    function transferFrom(address from, address to, uint value) public returns (bool success);

    /// @notice Approve spender to withdraw from your account, multiple times, up to the `value` amount.
    /// @param spender Address authorized to spend on your behalf
    /// @param value Maximum amount they can withdraw
    ///! @return success True if approval was successful
    function approve(address spender, uint value) public returns (bool success);

    /// @notice Returns the number of tokens owned by `owner`.
    /// @param owner Token owner
    /// @return balance Number of tokens owned by the owner
    function balanceOf(address owner) public view returns (uint balance);

    /// @notice Returns the amount of tokens that an owner has allowed another user to withdraw.
    /// @param owner Token owner
    /// @param spender Spender's address
    /// @return remaining Amount of remaining tokens allowed to be spent
    function allowance(address owner, address spender) public view returns (uint remaining);
}