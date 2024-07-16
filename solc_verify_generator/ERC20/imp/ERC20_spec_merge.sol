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
    /// @notice postcondition _remaining_ == nw._allowed[owner][spender]
    function allowance_post(address owner, address spender, uint256 _remaining_) public view  returns (uint256) {}

    /// @notice precondition true
    /// @notice postcondition true
    function balanceOf_pre(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition od._balances[owner] == balance
    /// @notice postcondition balance == nw._balances[owner]
    function balanceOf_post(address owner, uint256 balance) public view returns (uint256){}

    /// @notice precondition true
    /// @notice postcondition true
    function approve_pre(address spender, uint256 value, bool success) external returns (bool) {}

    /// @notice precondition forall (address addr1, address addr2) od._allowed[addr1][addr2] == nw._allowed[addr1][addr2] // Abs func 
    /// @notice precondition forall (address addr1, address addr2) od_old._allowed[addr1][addr2] == nw_old._allowed[addr1][addr2] // Abs func 
    /// @notice precondition (od._allowed[msg.sender][spender] == value && success) || (od._allowed[msg.sender][spender] == od_old._allowed[msg.sender][spender] && !success)
    /// @notice postcondition nw._allowed[msg.sender][spender] == value
    function approve_post(address spender, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition true
    /// @notice postcondition true
    function transfer_pre(address to, uint256 value, bool success) external returns (bool) {}
    
    /// @notice precondition forall (address addr) od._balances[addr] == nw._balances[addr] // Abs func 
    /// @notice precondition forall (address addr) od_old._balances[addr] == nw_old._balances[addr] // Abs func 
    /// @notice precondition (( od._balances[msg.sender] == od_old._balances[msg.sender] - value  && msg.sender != to) || (od._balances[msg.sender] == od_old._balances[msg.sender] && msg.sender == to ) && success ) || !success
    /// @notice precondition (( od._balances[to] == od_old._balances[to] + value && msg.sender != to ) || ( od._balances[to] == od_old._balances[to] && msg.sender == to ) && success ) || !success
    /// @notice postcondition nw._balances[msg.sender] == nw_old._balances[msg.sender] - value || nw._balances[msg.sender] == nw_old._balances[msg.sender]
    /// @notice postcondition nw._balances[to] == nw_old._balances[to] + value || nw._balances[to] == nw_old._balances[to]
    /// @notice postcondition value == 0 || to != address(0)
    /// @notice postcondition success
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
    /// @notice postcondition nw._balances[from] == nw_old._balances[from] - value || nw._balances[from] == nw_old._balances[from]
    /// @notice postcondition nw._balances[to] == nw_old._balances[to] + value || nw._balances[to] == nw_old._balances[to]
    /// @notice postcondition nw._allowed[from][msg.sender] == nw_old._allowed[from][msg.sender] - value || nw._allowed[from][msg.sender] == nw_old._allowed[from][msg.sender]
    /// @notice postcondition value == 0 || to != address(0)
    function transferFrom_post(address from, address to, uint256 value, bool success) external returns (bool) {}
}