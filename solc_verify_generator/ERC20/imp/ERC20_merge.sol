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

    function inv() public {}

    function cons_pre() public {}

    function cons_post() public {}

    ///@notice postcondition supply == con._totalSupply

    function totalSupply() public view returns (uint256 supply) {}

    ///@notice postcondition remaining == con._allowed[owner][spender]

    function allowance_post(address owner, address spender, uint256 remaining) public view  returns (uint256) {}

    ///@notice postcondition balance == con._balances[owner]

    function balanceOf_post(address owner, uint256 balance) public view returns (uint256){}

    ///@notice postcondition con._allowed[msg.sender][spender] == value

    function approve_post(address spender, uint256 value, bool success) external returns (bool) {}
    
    ///@notice postcondition con._balances[msg.sender] == con._balances[msg.sender] - value || con._balances[msg.sender] == con._balances[msg.sender]
/// @notice postcondition con._balances[to] == con._balances[to] + value || con._balances[to] == con._balances[to]
/// @notice postcondition con._balances[msg.sender] >= 0

	function transfer_post(address to, uint256 value, bool success) external returns (bool) {}

    ///@notice postcondition con._balances[from] == con._balances[from] - value || con._balances[from] == con._balances[from]
/// @notice postcondition con._balances[to] == con._balances[to] + value || con._balances[to] == con._balances[to]
/// @notice postcondition con._allowed[from][msg.sender] == con._allowed[from][msg.sender] - value || con._allowed[from][msg.sender] == con._allowed[from][msg.sender]
/// @notice postcondition con._balances[from] >= 0

    function transferFrom_post(address from, address to, uint256 value, bool success) external returns (bool) {}
}