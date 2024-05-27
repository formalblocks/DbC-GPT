// Juliandson specification was slightly changes to take into account different parameter
// and member variable names. Moreover, the emitting of events was removed for simplicity.

// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0;

contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);


    
    function transfer(address to, uint value) public returns (bool success);

    
    function transferFrom(address from, address to, uint value) public returns (bool success);

    function approve(address spender, uint value) public returns (bool success);

    function balanceOf(address owner) public view returns (uint balance);

    function allowance(address owner, address spender) public view returns (uint remaining);
}