pragma solidity >=0.5.7;

import "./IERC20.sol";
import "./math/SafeMath.sol";

contract ERC20 is IERC20 {
    using SafeMath for uint256;

    mapping (address => uint256) private _balances;

    mapping (address => mapping (address => uint256)) private _allowed;

    uint256 private _totalSupply;

    struct StateOld {
        uint256  _totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }

    struct StateNew {
        uint256  _totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }
    
    StateOld od;
    StateOld od_old;
    StateNew nw;
    StateNew nw_old;

    /// @notice precondition __verifier_sum_uint(od._balances) == od._totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(nw._balances) == nw._totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(od._balances) == __verifier_sum_uint(nw._balances) // Abs func 
    /// @notice postcondition supply == _totalSupply

    function totalSupply()  public view returns (uint256 supply) {
        return _totalSupply;
    }

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition od._balances[_owner] == balance
    /// @notice postcondition balance == _balances[_owner]
    
    function balanceOf(address _owner)  public view returns (uint256 balance) {
        return _balances[_owner];
    }

    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition od._allowed[_owner][_spender] == remaining
    /// @notice postcondition remaining == _allowed[_owner][_spender]
    
    function allowance(address _owner, address _spender)  public view returns (uint256 remaining) {
        return _allowed[_owner][_spender];
    }

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) od_old._balances[addr] == nw_old._balances[addr] // Abs func 
    /// @notice precondition (( od._balances[msg.sender] == od_old._balances[msg.sender] - _value  && msg.sender != _to) || (od._balances[msg.sender] == od_old._balances[msg.sender] && msg.sender == _to ) && success ) || !success
    /// @notice precondition (( od._balances[_to] == od_old._balances[_to] + _value && msg.sender != _to ) || ( od._balances[_to] == od_old._balances[_to] && msg.sender == _to ) && success ) || !success
    /// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - _value || _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender])
    /// @notice postcondition _balances[_to] == __verifier_old_uint(_balances[_to]) + _value || _balances[_to] == __verifier_old_uint(_balances[_to])
    /// @notice postcondition _value == 0 || _to != address(0)
    /// @notice postcondition success

    function transfer(address _to, uint256 _value)  public returns (bool success) {
        _transfer(msg.sender, _to, _value);
        return true;
    }

    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od_old._allowed[addr1][addr2] == nw_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (od._allowed[msg.sender][_spender] == _value && success) || (od._allowed[msg.sender][_spender] == od_old._allowed[msg.sender][_spender] && !success)
    /// @notice postcondition _allowed[msg.sender][_spender] == _value
    
    function approve(address _spender, uint256 _value)  public returns (bool success) {
        _approve(msg.sender, _spender, _value);
        return true;
    }

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) od_old._balances[addr] == nw_old._balances[addr] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od_old._allowed[addr1][addr2] == nw_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (( od._balances[msg.sender] == od_old._balances[msg.sender] - _value  && msg.sender != _to) || (od._balances[msg.sender] == od_old._balances[msg.sender] && msg.sender == _to ) && success ) || !success
    /// @notice precondition (( od._balances[_to] == od_old._balances[_to] + _value && msg.sender != _to ) || ( od._balances[_to] == od_old._balances[_to] && msg.sender == _to ) && success ) || !success
    /// @notice precondition (od._allowed[_from][msg.sender] == od_old._allowed[_from][msg.sender] - _value && success) || (od._allowed[_from ][msg.sender] == od_old._allowed[_from][msg.sender] && !success) || _from == msg.sender
    /// @notice precondition  od._allowed[_from][msg.sender] <= od_old._allowed[_from][msg.sender] || _from  == msg.sender

    /// @notice postcondition _balances[_from] == __verifier_old_uint(_balances[_from]) - _value || _balances[_from] == __verifier_old_uint(_balances[_from])
    /// @notice postcondition _balances[_to] == __verifier_old_uint(_balances[_to]) + _value || _balances[_to] == __verifier_old_uint(_balances[_to])
    /// @notice postcondition _allowed[_from][msg.sender] == __verifier_old_uint(_allowed[_from][msg.sender]) - _value || _allowed[_from][msg.sender] == __verifier_old_uint(_allowed[_from][msg.sender])
    /// @notice postcondition _value == 0 || _to != address(0)
    
    function transferFrom(address _from, address _to, uint256 _value)  public returns (bool success) {
        _transfer(_from, _to, _value);
        _approve(_from, msg.sender, _allowed[_from][msg.sender].sub(_value));
        return true;
    }

    /**
     * @dev Increase the amount of tokens that an owner allowed to a spender.
     * approve should be called when _allowed[msg.sender][spender] == 0. To increment
     * allowed value is better to use this function to avoid 2 calls (and wait until
     * the first transaction is mined)
     * From MonolithDAO Token.sol
     * Emits an Approval event.
     * @param spender The address which will spend the funds.
     * @param addedValue The amount of tokens to increase the allowance by.
     */
    function increaseAllowance(address spender, uint256 addedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowed[msg.sender][spender].add(addedValue));
        return true;
    }

    /**
     * @dev Decrease the amount of tokens that an owner allowed to a spender.
     * approve should be called when _allowed[msg.sender][spender] == 0. To decrement
     * allowed value is better to use this function to avoid 2 calls (and wait until
     * the first transaction is mined)
     * From MonolithDAO Token.sol
     * Emits an Approval event.
     * @param spender The address which will spend the funds.
     * @param subtractedValue The amount of tokens to decrease the allowance by.
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowed[msg.sender][spender].sub(subtractedValue));
        return true;
    }

    /**
     * @dev Transfer token for a specified addresses.
     * @param from The address to transfer from.
     * @param to The address to transfer to.
     * @param value The amount to be transferred.
     */
    function _transfer(address from, address to, uint256 value) internal {
        require(to != address(0));

        _balances[from] = _balances[from].sub(value);
        _balances[to] = _balances[to].add(value);
        emit Transfer(from, to, value);
    }

    /**
     * @dev Internal function that mints an amount of the token and assigns it to
     * an account. This encapsulates the modification of balances such that the
     * proper events are emitted.
     * @param account The account that will receive the created tokens.
     * @param value The amount that will be created.
     */
    function _mint(address account, uint256 value) internal {
        require(account != address(0));

        _totalSupply = _totalSupply.add(value);
        _balances[account] = _balances[account].add(value);
        emit Transfer(address(0), account, value);
    }

    /**
     * @dev Internal function that burns an amount of the token of a given
     * account.
     * @param account The account whose tokens will be burnt.
     * @param value The amount that will be burnt.
     */
    function _burn(address account, uint256 value) internal {
        require(account != address(0));

        _totalSupply = _totalSupply.sub(value);
        _balances[account] = _balances[account].sub(value);
        emit Transfer(account, address(0), value);
    }

    /**
     * @dev Approve an address to spend another addresses' tokens.
     * @param owner The address that owns the tokens.
     * @param spender The address that will spend the tokens.
     * @param value The number of tokens that can be spent.
     */
    function _approve(address owner, address spender, uint256 value) internal {
        require(spender != address(0));
        require(owner != address(0));

        _allowed[owner][spender] = value;
        emit Approval(owner, spender, value);
    }

    /**
     * @dev Internal function that burns an amount of the token of a given
     * account, deducting from the sender's allowance for said account. Uses the
     * internal burn function.
     * Emits an Approval event (reflecting the reduced allowance).
     * @param account The account whose tokens will be burnt.
     * @param value The amount that will be burnt.
     */
    function _burnFrom(address account, uint256 value) internal {
        _burn(account, value);
        _approve(account, msg.sender, _allowed[account][msg.sender].sub(value));
    }
}