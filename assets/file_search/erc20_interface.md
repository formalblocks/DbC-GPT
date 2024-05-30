```solidity
pragma solidity >=0.5.0;

contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed _from, address indexed _to, uint _value);
    event Approval(address indexed _owner, address indexed _spender, uint _value);

    function totalSupply() public view returns (uint256 supply);
    
    function transfer(address to, uint value) public returns (bool success);

    function transferFrom(address from, address to, uint value) public returns (bool success);

    function approve(address spender, uint value) public returns (bool success);

    function balanceOf(address owner) public view returns (uint balance);

    function allowance(address owner, address spender) public view returns (uint remaining);
}
```