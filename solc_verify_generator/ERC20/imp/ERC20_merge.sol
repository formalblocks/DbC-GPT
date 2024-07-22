// Based on: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/19c74140523e9af5a8489fe484456ca2adc87484/contracts/token/ERC20/ERC20.sol

contract Refinement {

    struct StateAbs {
        uint256  _totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }

    struct StateCon {
        uint256  _totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }
    
    StateAbs abs;
    StateAbs abs_old;
    StateCon con;
    StateCon con_old;

    /// @notice precondition __verifier_sum_uint(abs._balances) == abs._totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(con._balances) == con._totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(abs._balances) == __verifier_sum_uint(con._balances) // Abs func 
    /// @notice postcondition con._totalSupply == abs._totalSupply
    function inv() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function cons_pre() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function cons_post() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function allowance_pre(address _owner, address _spender, uint256 _remaining_) public view  returns (uint256) {}
    
    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    ///@notice precondition remaining == con._allowed[_owner][_spender]

    /// @notice postcondition abs._allowed[_owner][_spender] == remaining
    function allowance_post(address _owner, address _spender, uint256 remaining) public view  returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address _owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    ///@notice precondition balance == con._balances[_owner]

    /// @notice postcondition abs._balances[_owner] == balance
    function balanceOf_post(address _owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address _spender, uint256 _value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs_old._allowed[addr1][addr2] == con_old._allowed[addr1][addr2] // Abs func 
    ///@notice precondition con._allowed[msg.sender][_spender] == _value
/// @notice precondition success == true

    /// @notice postcondition (abs._allowed[msg.sender][_spender] == _value && success) || (abs._allowed[msg.sender][_spender] == abs_old._allowed[msg.sender][_spender] && !success)
    function approve_post(address _spender, uint256 _value, bool success) external returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transfer_pre(address _to, uint256 _value, bool success) external returns (bool) {}
    
    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) abs_old._balances[addr] == con_old._balances[addr] // Abs func 
    ///@notice precondition con._balances[msg.sender] == con_old._balances[msg.sender] - _value || con._balances[msg.sender] == con_old._balances[msg.sender]
/// @notice precondition con._balances[_to] == con_old._balances[_to] + _value || con._balances[_to] == con_old._balances[_to]
/// @notice precondition _value == 0 || _to != address(0)
/// @notice precondition msg.sender != _to || con._balances[msg.sender] >= _value

    /// @notice postcondition (( abs._balances[msg.sender] == abs_old._balances[msg.sender] - _value  && msg.sender != _to) || (abs._balances[msg.sender] == abs_old._balances[msg.sender] && msg.sender == _to ) && success ) || !success
    /// @notice postcondition (( abs._balances[_to] == abs_old._balances[_to] + _value && msg.sender != _to ) || ( abs._balances[_to] == abs_old._balances[_to] && msg.sender == _to ) && success ) || !success
	function transfer_post(address _to, uint256 _value, bool success) external returns (bool) {}

    /// @notice precondition true
    /// @notice postcondition true
    function transferFrom_pre(address _from, address _to, uint256 _value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) abs_old._balances[addr] == con_old._balances[addr] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs_old._allowed[addr1][addr2] == con_old._allowed[addr1][addr2] // Abs func 
    ///@notice precondition con._allowed[_from][msg.sender] == con_old._allowed[_from][msg.sender] - _value || con._allowed[_from][msg.sender] == con_old._allowed[_from][msg.sender]
/// @notice precondition con._balances[_from] == con_old._balances[_from] - _value || con._balances[_from] == con_old._balances[_from]
/// @notice precondition con._balances[_to] == con_old._balances[_to] + _value || con._balances[_to] == con_old._balances[_to]
/// @notice precondition _value == 0 || _to != address(0)

    /// @notice postcondition (( abs._balances[msg.sender] == abs_old._balances[msg.sender] - _value  && msg.sender != _to) || (abs._balances[msg.sender] == abs_old._balances[msg.sender] && msg.sender == _to ) && success ) || !success
    /// @notice postcondition (( abs._balances[_to] == abs_old._balances[_to] + _value && msg.sender != _to ) || ( abs._balances[_to] == abs_old._balances[_to] && msg.sender == _to ) && success ) || !success
    /// @notice postcondition (abs._allowed[_from][msg.sender] == abs_old._allowed[_from][msg.sender] - _value && success) || (abs._allowed[_from][msg.sender] == abs_old._allowed[_from][msg.sender] && !success) || _from == msg.sender
    /// @notice postcondition  abs._allowed[_from][msg.sender] <= abs_old._allowed[_from][msg.sender] || _from  == msg.sender
    function transferFrom_post(address _from, address _to, uint256 _value, bool success) external returns (bool) {}
}