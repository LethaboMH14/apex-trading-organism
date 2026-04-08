// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title ReputationRegistry
 * @dev Reputation management contract for APEX agents
 * @author DR. PRIYA NAIR - VP of Trust & Compliance at APEX
 * @notice Manages agent reputation scores with on-chain tracking
 */
contract ReputationRegistry is Ownable, ReentrancyGuard {
    
    // Structs
    struct ReputationEntry {
        uint256 timestamp;
        uint256 score;
        string tradeId;
        bytes32 outcomeHash;
    }
    
    // State variables
    mapping(uint256 => uint256) private _reputationScores;
    mapping(uint256 => ReputationEntry[]) private _reputationHistory;
    mapping(address => bool) private _authorizedCallers;
    
    uint256 private constant MIN_SCORE = 0;
    uint256 private constant MAX_SCORE = 100;
    uint256 private constant MAX_HISTORY_ENTRIES = 100;
    
    // Events
    event ReputationUpdated(
        uint256 indexed agentTokenId,
        uint256 newScore,
        string tradeId
    );
    
    /**
     * @dev Constructor
     */
    constructor() Ownable(msg.sender) {
        // Authorize contract owner by default
        _authorizedCallers[msg.sender] = true;
    }
    
    /**
     * @notice Update reputation score for an agent
     * @dev Only authorized callers can update reputation
     * @param agentTokenId The token ID of the agent
     * @param delta The score change (positive or negative)
     * @param tradeId The trade identifier
     * @param outcomeHash Hash of the trade outcome data
     */
    function updateReputation(
        uint256 agentTokenId,
        int8 delta,
        string calldata tradeId,
        bytes32 outcomeHash
    ) external nonReentrant onlyAuthorized {
        require(agentTokenId > 0, "ReputationRegistry: Invalid token ID");
        require(bytes(tradeId).length > 0, "ReputationRegistry: Trade ID required");
        
        uint256 currentScore = _reputationScores[agentTokenId];
        int256 newScoreInt = int256(currentScore) + int256(delta);
        
        // Enforce score bounds
        if (newScoreInt < int256(MIN_SCORE)) {
            newScoreInt = int256(MIN_SCORE);
        } else if (newScoreInt > int256(MAX_SCORE)) {
            newScoreInt = int256(MAX_SCORE);
        }
        
        uint256 newScore = uint256(newScoreInt);
        _reputationScores[agentTokenId] = newScore;
        
        // Add to history
        ReputationEntry memory entry = ReputationEntry({
            timestamp: block.timestamp,
            score: newScore,
            tradeId: tradeId,
            outcomeHash: outcomeHash
        });
        
        _reputationHistory[agentTokenId].push(entry);
        
        // Limit history size
        if (_reputationHistory[agentTokenId].length > MAX_HISTORY_ENTRIES) {
            // Remove oldest entry
            for (uint256 i = 0; i < _reputationHistory[agentTokenId].length - 1; i++) {
                _reputationHistory[agentTokenId][i] = _reputationHistory[agentTokenId][i + 1];
            }
            _reputationHistory[agentTokenId].pop();
        }
        
        emit ReputationUpdated(agentTokenId, newScore, tradeId);
    }
    
    /**
     * @notice Get the current reputation score for an agent
     * @param agentTokenId The token ID of the agent
     * @return Current reputation score (0-100)
     */
    function getReputation(uint256 agentTokenId) 
        external 
        view 
        returns (uint256) 
    {
        return _reputationScores[agentTokenId];
    }
    
    /**
     * @notice Get reputation history for an agent
     * @param agentTokenId The token ID of the agent
     * @return Array of reputation entries
     */
    function getHistory(uint256 agentTokenId) 
        external 
        view 
        returns (ReputationEntry[] memory) 
    {
        return _reputationHistory[agentTokenId];
    }
    
    /**
     * @notice Get the most recent reputation entry for an agent
     * @param agentTokenId The token ID of the agent
     * @return Most recent reputation entry
     */
    function getLastEntry(uint256 agentTokenId) 
        external 
        view 
        returns (ReputationEntry memory) 
    {
        ReputationEntry[] storage history = _reputationHistory[agentTokenId];
        require(history.length > 0, "ReputationRegistry: No history found");
        return history[history.length - 1];
    }
    
    /**
     * @notice Authorize an address to update reputation
     * @dev Only contract owner can authorize callers
     * @param caller The address to authorize
     * @param authorized Whether to authorize or deauthorize
     */
    function setAuthorizedCaller(address caller, bool authorized) 
        external 
        onlyOwner 
    {
        _authorizedCallers[caller] = authorized;
    }
    
    /**
     * @notice Check if an address is authorized to update reputation
     * @param caller The address to check
     * @return True if authorized
     */
    function isAuthorized(address caller) 
        external 
        view 
        returns (bool) 
    {
        return _authorizedCallers[caller];
    }
    
    /**
     * @notice Get score bounds
     * @return Minimum and maximum possible scores
     */
    function getScoreBounds() 
        external 
        pure 
        returns (uint256 minScore, uint256 maxScore) 
    {
        return (MIN_SCORE, MAX_SCORE);
    }
    
    // Modifier
    modifier onlyAuthorized() {
        require(_authorizedCallers[msg.sender], "ReputationRegistry: Caller not authorized");
        _;
    }
}
