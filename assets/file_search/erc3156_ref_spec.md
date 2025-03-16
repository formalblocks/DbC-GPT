pragma solidity >= 0.5.0;


interface VatLike {
    function dai(address) external view returns (uint256);
    function move(address src, address dst, uint256 rad) external;
    function heal(uint256 rad) external;
    function suck(address,address,uint256) external;
}

contract ERC3156FlashLender {

    // --- Auth ---
    function rely(address guy) external auth { wards[guy] = 1; emit Rely(guy); }
    function deny(address guy) external auth { wards[guy] = 0; emit Deny(guy); }
    mapping (address => uint256) public wards;
    modifier auth {
        require(wards[msg.sender] == 1, "DssFlash/not-authorized");
        _;
    }

    // --- Data ---
    VatAbstract public         vat;
    address public             vow;
    DaiJoinAbstract public     daiJoin;
    DaiAbstract public         dai;
    
    uint256 public                      line;       // Debt Ceiling  [wad]
    uint256 public                      toll;       // Fee           [wad]
    uint256 private                     locked;     // Reentrancy guard

    // --- Events ---
    event Rely(address indexed usr);
    event Deny(address indexed usr);
    event File(bytes32 indexed what, uint256 data);
    event File(bytes32 indexed what, address data);
    event FlashLoan(address indexed receiver, address token, uint256 amount, uint256 fee);
    event VatDaiFlashLoan(address indexed receiver, uint256 amount, uint256 fee);

    modifier lock {
        require(locked == 0, "DssFlash/reentrancy-guard");
        locked = 1;
        _;
        locked = 0;
    }

    // --- Init ---
    constructor(address vat_, address vow_, address daiJoin_) public {
        wards[msg.sender] = 1;
        emit Rely(msg.sender);

        vat = VatAbstract(vat_);
        vow = vow_;
        daiJoin = DaiJoinAbstract(daiJoin_);
        dai = DaiAbstract(DaiJoinAbstract(daiJoin_).dai());

        VatAbstract(vat_).hope(daiJoin_);
        DaiAbstract(DaiJoinAbstract(daiJoin_).dai()).approve(daiJoin_, uint256(-1));
    }

    // --- Math ---
    uint256 constant WAD = 10 ** 18;
    uint256 constant RAY = 10 ** 27;
    uint256 constant RAD = 10 ** 45;
    function add(uint256 x, uint256 y) internal pure returns (uint256 z);

    function mul(uint256 x, uint256 y) internal pure returns (uint256 z);

    /// @notice postcondition maxLoan == line && token == address(dai) || maxLoan == 0 
    function maxFlashLoan(address token) external  view returns (uint256 maxLoan);

    /// @notice postcondition token == address(dai)
    /// @notice postcondition fee == (amount * toll) / WAD
    function flashFee(address token, uint256 amount) external  view returns (uint256 fee);

    ///  @notice postcondition token == address(dai)
    ///  @notice postcondition amount <= line
    ///  @notice postcondition __verifier_old_address (token) == token
    ///  @notice postcondition __verifier_old_uint (amount) == amount
    ///  @notice postcondition flash == true
    function flashLoan(IERC3156FlashBorrower receiver, address token, uint256 amount, bytes calldata data) external lock returns (bool flash);

    // --- Vat Dai Flash Loan ---
    function vatDaiFlashLoan(
        IVatDaiFlashLoanReceiver receiver,      // address of conformant IVatDaiFlashLoanReceiver
        uint256 amount,                         // amount to flash loan [rad]
        bytes calldata data                     // arbitrary data to pass to the receiver
    ) external lock;
}
