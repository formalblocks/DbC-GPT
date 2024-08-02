// Based on: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/19c74140523e9af5a8489fe484456ca2adc87484/contracts/token/ERC20/ERC20.sol

contract Refinement {

    struct StateAbs {
        uint256  totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }

    struct StateCon {
        uint256  totalSupply;
        mapping (address => uint256) _balances;
        mapping (address => mapping (address => uint256)) _allowed;
    }
    
    StateAbs abs;
    StateAbs abs_old;
    StateCon con;
    StateCon con_old;

    /// @notice precondition __verifier_sum_uint(abs._balances) == abs.totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(con._balances) == con.totalSupply // Abs func 
    /// @notice precondition __verifier_sum_uint(abs._balances) == __verifier_sum_uint(con._balances) // Abs func 
    /// @notice postcondition con.totalSupply == abs.totalSupply
    function inv() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function cons_pre() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function cons_post() public {}

    /// @notice precondition true
    /// @notice postcondition true
    function allowance_pre(address owner, address spender, uint256 _remaining_) public view  returns (uint256) {}
    
    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    /// @notice precondition abs._allowed[owner][spender] == remaining
    ///@notice postcondition remaining == con._allowed[owner][spender]

    function allowance_post(address owner, address spender, uint256 remaining) public view  returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    /// @notice precondition abs._balances[owner] == balance
    ///@notice postcondition balance == con._balances[owner]

    function balanceOf_post(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address spender, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs_old._allowed[addr1][addr2] == con_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (abs._allowed[msg.sender][spender] == value && success) || (abs._allowed[msg.sender][spender] == abs_old._allowed[msg.sender][spender] && !success)
    ///@notice postcondition con._allowed[msg.sender][spender] == value

    function approve_post(address spender, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transfer_pre(address to, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) abs_old._balances[addr] == con_old._balances[addr] // Abs func 
    /// @notice precondition (( abs._balances[msg.sender] == abs_old._balances[msg.sender] - value  && msg.sender != to) || (abs._balances[msg.sender] == abs_old._balances[msg.sender] && msg.sender == to ) && success ) || !success
    /// @notice precondition (( abs._balances[to] == abs_old._balances[to] + value && msg.sender != to ) || ( abs._balances[to] == abs_old._balances[to] && msg.sender == to ) && success ) || !success
    ///@notice postcondition con._balances[msg.sender] == con._balances[msg.sender] - value || con._balances[msg.sender] == con._balances[msg.sender]
/// @notice postcondition con._balances[to] == con._balances[to] + value || con._balances[to] == con._balances[to]
/// @notice postcondition con._balances[msg.sender] >= 0

	function transfer_post(address to, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition true
    /// @notice postcondition true
    function transferFrom_pre(address from, address to, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr) abs._balances[addr] == con._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) abs_old._balances[addr] == con_old._balances[addr] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs._allowed[addr1][addr2] == con._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) abs_old._allowed[addr1][addr2] == con_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (( abs._balances[from] == abs_old._balances[from] - value  && from != to) || (abs._balances[from] == abs_old._balances[from] && from == to ) && success ) || !success
    /// @notice precondition (( abs._balances[to] == abs_old._balances[to] + value && from != to ) || ( abs._balances[to] == abs_old._balances[to] && from == to ) && success ) || !success
    /// @notice precondition (abs._allowed[from][msg.sender] == abs_old._allowed[from][msg.sender] - value && success) || (abs._allowed[from][msg.sender] == abs_old._allowed[from][msg.sender] && !success) || from == msg.sender
    /// @notice precondition  abs._allowed[from][msg.sender] <= abs_old._allowed[from][msg.sender] || from  == msg.sender
    ///@notice postcondition con._balances[from] == con._balances[from] - value || con._balances[from] == con._balances[from]
/// @notice postcondition con._balances[to] == con._balances[to] + value || con._balances[to] == con._balances[to]
/// @notice postcondition con._allowed[from][msg.sender] == con._allowed[from][msg.sender] - value || con._allowed[from][msg.sender] == con._allowed[from][msg.sender]
/// @notice postcondition con._balances[from] >= 0

    function transferFrom_post(address from, address to, uint256 value, bool success) external returns (bool) {}
}