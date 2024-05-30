```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.5.7;

contract ERC20 {

    mapping (address => uint) _balances;
    mapping (address => mapping (address => uint)) _allowed;
    uint public _totalSupply;

    event Transfer(address indexed _from, address indexed _to, uint _value);
    event Approval(address indexed _owner, address indexed _spender, uint _value);

    /// @notice postcondition supply == _totalSupply
    function totalSupply() public view returns (uint256 supply);

    /// @notice  postcondition ( ( _balances[msg.sender] ==  __verifier_old_uint (_balances[msg.sender] ) - _value  && msg.sender  != _to ) ||   ( _balances[msg.sender] ==  __verifier_old_uint ( _balances[msg.sender]) && msg.sender  == _to ) &&  success )   || !success
    /// @notice  postcondition ( ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) + _value  && msg.sender  != _to ) ||   ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) && msg.sender  == _to )  )   || !success
    function transfer(address _to, uint256 _value) public returns (bool success);

    /// @notice  postcondition ( ( _balances[_from] ==  __verifier_old_uint (_balances[_from] ) - _value  &&  _from  != _to ) || ( _balances[_from] ==  __verifier_old_uint ( _balances[_from] ) &&  _from == _to ) && success ) || !success 
    /// @notice  postcondition ( ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) + _value  &&  _from  != _to ) || ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) &&  _from  == _to ) && success ) || !success 
    /// @notice  postcondition ( _allowed[_from ][msg.sender] ==  __verifier_old_uint (_allowed[_from ][msg.sender] ) - _value && success) || ( _allowed[_from ][msg.sender] ==  __verifier_old_uint (_allowed[_from ][msg.sender]) && !success) ||  _from  == msg.sender
    /// @notice  postcondition  _allowed[_from ][msg.sender]  <= __verifier_old_uint (_allowed[_from ][msg.sender] ) ||  _from  == msg.sender
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

    /// @notice  postcondition (_allowed[msg.sender ][ _spender] ==  _value  &&  success) || ( _allowed[msg.sender ][ _spender] ==  __verifier_old_uint ( _allowed[msg.sender ][ _spender] ) && !success )    
    function approve(address _spender, uint256 _value) public returns (bool success);

    /// @notice postcondition _balances[_owner] == balance
    function balanceOf(address _owner) public view returns (uint256 balance);

    /// @notice postcondition _allowed[_owner][_spender] == remaining
    function allowance(address _owner, address _spender) public view returns (uint256 remaining);
}
```