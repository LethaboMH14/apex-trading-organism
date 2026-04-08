// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title ValidationRegistry
 * @dev Validation artifact registry for APEX trade decisions
 * @author DR. PRIYA NAIR - VP of Trust & Compliance at APEX
 * @notice Manages validation artifacts with EIP-712 signature verification
 */
contract ValidationRegistry is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;
    
    // Structs
    struct ValidationRecord {
        bytes32 reasoningChainHash;
        bytes eip712Signature;
        string tradeId;
        uint256 timestamp;
        address validator;
        bool verified;
    }
    
    // State variables
    mapping(uint256 => ValidationRecord) private _validations;
    mapping(address => bool) private _authorizedValidators;
    uint256 private _nextValidationId;
    
    // Domain separator for EIP-712
    bytes32 private immutable _domainSeparator;
    
    // EIP-712 type hash
    bytes32 private constant _VALIDATION_TYPEHASH = keccak256(
        "ValidationRecord(bytes32 reasoningChainHash,bytes eip712Signature,string tradeId,uint256 timestamp,address validator)"
    );
    
    // Events
    event ValidationSubmitted(
        uint256 indexed validationId,
        string tradeId,
        bytes32 reasoningChainHash
    );
    
    event ValidationVerified(
        uint256 indexed validationId,
        bool verified
    );
    
    /**
     * @dev Constructor
     */
    constructor() Ownable(msg.sender) {
        _nextValidationId = 1;
        _domainSeparator = _buildDomainSeparator();
        
        // Authorize contract owner by default
        _authorizedValidators[msg.sender] = true;
    }
    
    /**
     * @notice Submit a validation artifact
     * @dev Only authorized validators can submit validations
     * @param reasoningChainHash Hash of the complete reasoning chain
     * @param eip712Signature EIP-712 signature of the validation
     * @param tradeId The trade identifier
     * @return validationId The ID of the submitted validation
     */
    function submitValidation(
        bytes32 reasoningChainHash,
        bytes memory eip712Signature,
        string calldata tradeId
    ) external nonReentrant onlyAuthorized returns (uint256 validationId) {
        require(reasoningChainHash != bytes32(0), "ValidationRegistry: Reasoning hash required");
        require(eip712Signature.length > 0, "ValidationRegistry: Signature required");
        require(bytes(tradeId).length > 0, "ValidationRegistry: Trade ID required");
        
        validationId = _nextValidationId;
        _nextValidationId++;
        
        // Create validation record
        ValidationRecord storage validation = _validations[validationId];
        validation.reasoningChainHash = reasoningChainHash;
        validation.eip712Signature = eip712Signature;
        validation.tradeId = tradeId;
        validation.timestamp = block.timestamp;
        validation.validator = msg.sender;
        validation.verified = false; // Requires explicit verification
        
        emit ValidationSubmitted(validationId, tradeId, reasoningChainHash);
    }
    
    /**
     * @notice Verify a validation record
     * @dev Anyone can verify, but verification is recorded
     * @param validationId The ID of the validation to verify
     * @return True if the signature is valid
     */
    function verifyValidation(uint256 validationId) 
        external 
        returns (bool) 
    {
        require(_validations[validationId].timestamp != 0, "ValidationRegistry: Validation does not exist");
        
        ValidationRecord storage validation = _validations[validationId];
        
        // Reconstruct the signed message
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                _VALIDATION_TYPEHASH,
                validation.reasoningChainHash,
                keccak256(validation.eip712Signature),
                keccak256(bytes(validation.tradeId)),
                validation.timestamp,
                validation.validator
            )
        );
        
        // Recover the signer address
        address recoveredSigner = messageHash.toEthSignedMessageHash().recover(
            validation.eip712Signature
        );
        
        bool isValidSignature = recoveredSigner == validation.validator;
        validation.verified = isValidSignature;
        
        emit ValidationVerified(validationId, isValidSignature);
        
        return isValidSignature;
    }
    
    /**
     * @notice Get a validation record
     * @param validationId The ID of the validation
     * @return The validation record
     */
    function getValidation(uint256 validationId) 
        external 
        view 
        returns (ValidationRecord memory) 
    {
        require(_validations[validationId].timestamp != 0, "ValidationRegistry: Validation does not exist");
        return _validations[validationId];
    }
    
    /**
     * @notice Check if a validation has been verified
     * @param validationId The ID of the validation
     * @return True if verified
     */
    function isVerified(uint256 validationId) 
        external 
        view 
        returns (bool) 
    {
        return _validations[validationId].verified;
    }
    
    /**
     * @notice Get all validations for a trade
     * @param tradeId The trade identifier
     * @param maxResults Maximum number of results to return
     * @return Array of validation IDs
     */
    function getValidationsForTrade(string calldata tradeId, uint256 maxResults) 
        external 
        view 
        returns (uint256[] memory) 
    {
        uint256[] memory result = new uint256[](maxResults);
        uint256 count = 0;
        
        // This is inefficient for production - in practice, you'd want a mapping from tradeId to validationIds
        for (uint256 i = 1; i < _nextValidationId && count < maxResults; i++) {
            if (keccak256(bytes(_validations[i].tradeId)) == keccak256(bytes(tradeId))) {
                result[count] = i;
                count++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory finalResult = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResult[i] = result[i];
        }
        
        return finalResult;
    }
    
    /**
     * @notice Authorize an address to submit validations
     * @dev Only contract owner can authorize validators
     * @param validator The address to authorize
     * @param authorized Whether to authorize or deauthorize
     */
    function setAuthorizedValidator(address validator, bool authorized) 
        external 
        onlyOwner 
    {
        _authorizedValidators[validator] = authorized;
    }
    
    /**
     * @notice Check if an address is authorized to submit validations
     * @param validator The address to check
     * @return True if authorized
     */
    function isAuthorizedValidator(address validator) 
        external 
        view 
        returns (bool) 
    {
        return _authorizedValidators[validator];
    }
    
    /**
     * @notice Get the next validation ID
     * @return The next validation ID that will be assigned
     */
    function getNextValidationId() 
        external 
        view 
        returns (uint256) 
    {
        return _nextValidationId;
    }
    
    /**
     * @notice Build domain separator for EIP-712
     * @return Domain separator hash
     */
    function _buildDomainSeparator() internal view returns (bytes32) {
        return keccak256(
            abi.encodePacked(
                "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)",
                keccak256(bytes("APEX Validation Registry")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }
    
    // Modifiers
    modifier onlyAuthorized() {
        require(_authorizedValidators[msg.sender], "ValidationRegistry: Caller not authorized");
        _;
    }
}
