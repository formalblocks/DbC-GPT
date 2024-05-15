// Juliandson specification was slightly changes to take into account different parameter
// and member variable names. Moreover, the emitting of events was removed for simplicity.

// SPDX-License-Identifier: MIT
pragma solidity >=0.5.7;

/// @notice  invariant  _totalSupply  ==  __verifier_sum_uint(_balances)
contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);


    /// @notice  postcondition ( ( _balances[msg.sender] ==  __verifier_old_uint (_balances[msg.sender] ) - value  && msg.sender  != to ) ||   ( _balances[msg.sender] ==  __verifier_old_uint ( _balances[msg.sender]) && msg.sender  == to ) &&  success )   || !success
    /// @notice  postcondition ( ( _balances[to] ==  __verifier_old_uint ( _balances[to] ) + value  && msg.sender  != to ) ||   ( _balances[to] ==  __verifier_old_uint ( _balances[to] ) && msg.sender  == to )  )   || !success
    function transfer(address to, uint value) public returns (bool success);

    /// @notice  postcondition ( ( _balances[from] ==  __verifier_old_uint (_balances[from] ) - value  &&  from  != to ) || ( _balances[from] ==  __verifier_old_uint ( _balances[from] ) &&  from == to ) && success ) || !success 
    /// @notice  postcondition ( ( _balances[to] ==  __verifier_old_uint ( _balances[to] ) + value  &&  from  != to ) || ( _balances[to] ==  __verifier_old_uint ( _balances[to] ) &&  from  == to ) && success ) || !success 
    /// @notice  postcondition ( _allowed[from ][msg.sender] ==  __verifier_old_uint (_allowed[from ][msg.sender] ) - value && success) || ( _allowed[from ][msg.sender] ==  __verifier_old_uint (_allowed[from ][msg.sender]) && !success) ||  from  == msg.sender
    /// @notice  postcondition  _allowed[from ][msg.sender]  <= __verifier_old_uint (_allowed[from ][msg.sender] ) ||  from  == msg.sender
    function transferFrom(address from, address to, uint value) public returns (bool success);

    /// @notice  postcondition (_allowed[msg.sender ][ spender] ==  value  &&  success) || ( _allowed[msg.sender ][ spender] ==  __verifier_old_uint ( _allowed[msg.sender ][ spender] ) && !success )    
    function approve(address spender, uint value) public returns (bool success);

    /// @notice postcondition _balances[owner] == balance
    function balanceOf(address owner) public view returns (uint balance);

      /// @notice postcondition _allowed[owner][spender] == remaining
    function allowance(address owner, address spender) public view returns (uint remaining);
}