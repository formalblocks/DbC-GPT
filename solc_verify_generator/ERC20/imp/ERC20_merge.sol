// Based on: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/19c74140523e9af5a8489fe484456ca2adc87484/contracts/token/ERC20/ERC20.sol

contract Refinement {

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
    /// @notice postcondition nw._totalSupply == od._totalSupply
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
    
    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition od._allowed[owner][spender] == _remaining_
    ///@notice Returns the amount which _spender is still allowed to withdraw from _owner
/// @param owner The address who owns the funds
///t @param spender The address who will spend the funds
/// @return remaining An uint specifying the amount still allowed to be spent

    function allowance_post(address owner, address spender, uint256 _remaining_) public view  returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition od._balances[owner] == balance
    ///@notice Get the balance of the specified address
/// @param owner The address to query the the balance of
/// @return balance The balance

    function balanceOf_post(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address spender, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od_old._allowed[addr1][addr2] == nw_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (od._allowed[msg.sender][spender] == value && success) || (od._allowed[msg.sender][spender] == od_old._allowed[msg.sender][spender] && !success)
    ///@notice Approve the passed address to spend the specified amount of tokens on behalf of msg.sender
/// @param spender The address which will spend the funds
/// @param value The amount of tokens to be spent
/// @return success True if the function call was successful

    function approve_post(address spender, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transfer_pre(address to, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) od_old._balances[addr] == nw_old._balances[addr] // Abs func 
    /// @notice precondition (( od._balances[msg.sender] == od_old._balances[msg.sender] - value  && msg.sender != to) || (od._balances[msg.sender] == od_old._balances[msg.sender] && msg.sender == to ) && success ) || !success
    /// @notice precondition (( od._balances[to] == od_old._balances[to] + value && msg.sender != to ) || ( od._balances[to] == od_old._balances[to] && msg.sender == to ) && success ) || !success
    ///@notice Transfer tokens from the caller to a specified address
/// @param to The address to transfer to
/// @param value The amount to be transferred
/// @return success True if the transfer was successful

	function transfer_post(address to, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition true
    /// @notice postcondition true
    function transferFrom_pre(address from, address to, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) od_old._balances[addr] == nw_old._balances[addr] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od_old._allowed[addr1][addr2] == nw_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (( od._balances[msg.sender] == od_old._balances[msg.sender] - value  && msg.sender != to) || (od._balances[msg.sender] == od_old._balances[msg.sender] && msg.sender == to ) && success ) || !success
    /// @notice precondition (( od._balances[to] == od_old._balances[to] + value && msg.sender != to ) || ( od._balances[to] == od_old._balances[to] && msg.sender == to ) && success ) || !success
    /// @notice precondition (od._allowed[from][msg.sender] == od_old._allowed[from][msg.sender] - value && success) || (od._allowed[from ][msg.sender] == od_old._allowed[from][msg.sender] && !success) || from == msg.sender
    /// @notice precondition  od._allowed[from][msg.sender] <= od_old._allowed[from][msg.sender] || from  == msg.sender
    ///@notice Transfer tokens from one address to another
/// @param from The address which you want to send tokens from
/// @param to The address to transfer to
/// @param value The amount of tokens to be transferred
/// @return success True if the transfer was successful

    function transferFrom_post(address from, address to, uint256 value, bool success) external returns (bool) {}
}