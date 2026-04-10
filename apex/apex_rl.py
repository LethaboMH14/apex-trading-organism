"""
APEX Reinforcement Learning - Strategy Evolution System

DR. LIN QIANRU: Chief Learning Officer of APEX.

Background: Taiwanese-South African. MIT Media Lab PhD. Former Google Brain researcher.
Specializes in reinforcement learning for financial markets.

This module implements complete RL environment for APEX including trading environment,
PPO training, and strategy mutation. The system continuously evolves trading strategies
through reinforcement learning and genetic algorithms.

Author: DR. LIN QIANRU
Standard: "A strategy that cannot learn from its own failures is not a strategy."
"""

import asyncio
import json
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from gym import spaces
from collections import deque
import random

# APEX imports
from dotenv import load_dotenv, find_dotenv
from apex_llm_router import ask_lin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(find_dotenv(), override=True)


@dataclass
class TradingState:
    """Trading state representation for RL environment."""
    price_momentum: float
    sentiment_score: float
    prism_signal: float
    volume_anomaly: float
    on_chain_signal: float
    current_position: float  # -1 to 1 (short to long)
    unrealized_pnl: float
    time_of_day_normalized: float  # 0 to 1


class TradingEnvironment:
    """OpenAI Gym-compatible trading environment for APEX RL."""
    
    def __init__(self):
        """Initialize trading environment."""
        self.action_space = spaces.Discrete(4)  # 0=hold, 1=buy, 2=sell, 3=close
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(8,), dtype=np.float32)
        
        # Environment state
        self.current_state = None
        self.current_position = 0.0
        self.unrealized_pnl = 0.0
        self.entry_price = 0.0
        self.current_price = 100.0
        self.time_step = 0
        self.max_steps = 1000
        
        # Performance tracking
        self.total_reward = 0.0
        self.episode_rewards = []
        self.sharpe_history = []
        
        logger.info("🎮 TradingEnvironment initialized")
    
    def _get_state_vector(self) -> np.ndarray:
        """Get current state as numpy array."""
        # Generate mock signals for demonstration
        price_momentum = np.random.normal(0, 0.1)
        sentiment_score = np.random.normal(0, 0.2)
        prism_signal = np.random.normal(0, 0.15)
        volume_anomaly = np.random.normal(0, 0.1)
        on_chain_signal = np.random.normal(0, 0.1)
        time_of_day = (self.time_step % 24) / 24.0
        
        state = np.array([
            price_momentum,
            sentiment_score,
            prism_signal,
            volume_anomaly,
            on_chain_signal,
            self.current_position,
            self.unrealized_pnl,
            time_of_day
        ], dtype=np.float32)
        
        return state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        self.time_step += 1
        
        # Get current state
        current_state = self._get_state_vector()
        
        # Execute action
        reward = 0.0
        done = False
        
        if action == 1:  # Buy
            if self.current_position < 0.5:  # Max position limit
                self.current_position += 0.1
                self.entry_price = self.current_price
                logger.debug(f"📈 BUY at {self.current_price}")
                
        elif action == 2:  # Sell
            if self.current_position > -0.5:  # Max short limit
                self.current_position -= 0.1
                self.entry_price = self.current_price
                logger.debug(f"📉 SELL at {self.current_price}")
                
        elif action == 3:  # Close position
            if abs(self.current_position) > 0.01:
                realized_pnl = self.current_position * (self.current_price - self.entry_price)
                reward = realized_pnl * 10  # Scale reward
                self.total_reward += reward
                self.current_position = 0.0
                self.unrealized_pnl = 0.0
                logger.debug(f"🔄 CLOSE position, PnL: {realized_pnl:.4f}")
        
        # Update price (random walk for demonstration)
        price_change = np.random.normal(0, 0.01)
        self.current_price *= (1 + price_change)
        
        # Update unrealized PnL
        if abs(self.current_position) > 0.01:
            self.unrealized_pnl = self.current_position * (self.current_price - self.entry_price)
        
        # Risk-adjusted reward (Sharpe-weighted)
        if len(self.episode_rewards) > 10:
            recent_rewards = self.episode_rewards[-10:]
            sharpe_weight = np.mean(recent_rewards) / (np.std(recent_rewards) + 1e-6)
            reward *= (1 + 0.1 * sharpe_weight)
        
        self.episode_rewards.append(reward)
        
        # Check if episode is done
        done = self.time_step >= self.max_steps or abs(self.unrealized_pnl) > 0.2
        
        # Get next state
        next_state = self._get_state_vector()
        
        # Info dictionary
        info = {
            "current_price": self.current_price,
            "position": self.current_position,
            "unrealized_pnl": self.unrealized_pnl,
            "total_reward": self.total_reward,
            "time_step": self.time_step
        }
        
        return next_state, reward, done, info
    
    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.current_position = 0.0
        self.unrealized_pnl = 0.0
        self.entry_price = 0.0
        self.current_price = 100.0
        self.time_step = 0
        self.total_reward = 0.0
        self.episode_rewards = []
        
        # Random starting point
        self.current_price *= np.random.uniform(0.9, 1.1)
        
        state = self._get_state_vector()
        logger.info("🔄 Environment reset")
        return state
    
    def render(self, mode='human'):
        """Render environment state."""
        if mode == 'human':
            print(f"Step: {self.time_step}, Price: {self.current_price:.2f}, "
                  f"Position: {self.current_position:.2f}, "
                  f"Unrealized PnL: {self.unrealized_pnl:.4f}")


class ApexPolicyNetwork(nn.Module):
    """Neural network for PPO policy."""
    
    def __init__(self, state_dim: int = 8, action_dim: int = 4, hidden_dim: int = 64):
        """Initialize policy network."""
        super(ApexPolicyNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, action_dim)
        
        # Value head
        self.value_head = nn.Linear(hidden_dim // 2, 1)
        
        logger.info("🧠 ApexPolicyNetwork initialized")
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through network."""
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        
        # Policy logits
        logits = self.fc3(x)
        
        # Value estimate
        value = self.value_head(x)
        
        return logits, value
    
    def get_action_tensor(self, state: torch.Tensor) -> Tuple[int, torch.Tensor, torch.Tensor]:
        """Get action from policy network (original tensor-based method)."""
        logits, value = self.forward(state)
        probs = F.softmax(logits, dim=-1)
        
        # Sample action
        action = torch.multinomial(probs, 1).item()
        
        return action, probs, value
    
    def get_action(self, market_state: dict) -> str:
        """
        Called from apex_live.py with a market state dict.
        Returns "BUY", "SELL", or "HOLD" as a string.
        market_state keys: price, change_24h, sentiment_score
        """
        try:
            # Normalize inputs to [-1, 1] range
            price_momentum = float(market_state.get("change_24h", 0)) / 10.0
            sentiment = (float(market_state.get("sentiment_score", 50)) - 50) / 50.0
            price_norm = 0.0  # relative, no absolute reference needed
            
            # Build 8-dim state vector (pad with zeros for unused dims)
            state_vec = np.array([
                np.clip(price_momentum, -1, 1),
                np.clip(sentiment, -1, 1),
                0.0,  # prism_signal (not available here)
                0.0,  # volume_anomaly
                0.0,  # on_chain_signal
                0.0,  # current_position
                0.0,  # unrealized_pnl
                0.0   # time_of_day
            ], dtype=np.float32)
            
            state_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            
            with torch.no_grad():
                logits, _ = self.forward(state_tensor)
                probs = torch.softmax(logits, dim=-1).squeeze()
            
            action_idx = torch.argmax(probs).item()
            # Map: 0=HOLD, 1=BUY, 2=SELL, 3=HOLD (close maps to HOLD)
            action_map = {0: "HOLD", 1: "BUY", 2: "SELL", 3: "HOLD"}
            action = action_map.get(action_idx, "BUY")
            
            logger.debug(f"RL action: {action} (probs: {probs.tolist()})")
            return action
        except Exception as e:
            logger.warning(f"RL get_action failed: {e} — defaulting to BUY")
            return "BUY"
    
    def update(self, trade_outcome: dict):
        """
        Called after each trade to do a lightweight online update.
        trade_outcome keys: action, price, sentiment, success
        """
        try:
            # Build state from outcome
            sentiment = float(trade_outcome.get("sentiment", 50))
            change = float(trade_outcome.get("change_24h", 0))
            state_vec = np.array([
                np.clip(change / 10.0, -1, 1),
                np.clip((sentiment - 50) / 50.0, -1, 1),
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ], dtype=np.float32)
            
            state_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            
            # Reward: +1 if trade succeeded, -0.5 if failed
            reward = 1.0 if trade_outcome.get("success", False) else -0.5
            
            # Action index
            action_str = trade_outcome.get("action", "BUY")
            action_idx = {"HOLD": 0, "BUY": 1, "SELL": 2}.get(action_str, 1)
            
            # Simple policy gradient update
            if not hasattr(self, '_optimizer'):
                self._optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)
            
            logits, value = self.forward(state_tensor)
            probs = torch.softmax(logits, dim=-1)
            log_prob = torch.log(probs[0, action_idx] + 1e-8)
            
            # Policy gradient loss: -log_prob * reward
            loss = -log_prob * reward
            
            self._optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.parameters(), 0.5)
            self._optimizer.step()
            
            logger.debug(f"RL updated: action={action_str}, reward={reward:.2f}, loss={loss.item():.4f}")
            
            # Auto-save checkpoint after every 10 updates
            if not hasattr(self, '_update_count'):
                self._update_count = 0
            self._update_count += 1
            if self._update_count % 10 == 0:
                import os
                os.makedirs("apex/models", exist_ok=True)
                self.save_checkpoint("apex/models/policy_network.pt")
                
        except Exception as e:
            logger.warning(f"RL update failed: {e}")
    
    def save_checkpoint(self, path: str):
        """Save model checkpoint."""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'update_count': getattr(self, '_update_count', 0),
        }, path)
        logger.info(f"RL policy saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location='cpu', weights_only=True)
        self.load_state_dict(checkpoint['model_state_dict'])
        self._update_count = checkpoint.get('update_count', 0)
        logger.info(f"RL policy loaded from {path} (updates: {self._update_count})")


class PPOTrainer:
    """Proximal Policy Optimization trainer for APEX."""
    
    def __init__(self, env: TradingEnvironment):
        """Initialize PPO trainer."""
        self.env = env
        self.policy = ApexPolicyNetwork()
        self.optimizer = optim.Adam(self.policy.parameters(), lr=3e-4)
        
        # PPO hyperparameters
        self.clip_ratio = 0.2
        self.entropy_bonus = 0.01
        self.gamma = 0.99
        self.gae_lambda = 0.95
        self.ppo_epochs = 4
        self.batch_size = 64
        
        # Training metrics
        self.episode_rewards = []
        self.policy_losses = []
        self.value_losses = []
        
        logger.info("🎓 PPOTrainer initialized")
    
    def compute_gae(self, rewards: List[float], values: List[float], dones: List[bool]) -> Tuple[List[float], List[float]]:
        """Compute Generalized Advantage Estimation."""
        advantages = []
        returns = []
        
        gae = 0
        for i in reversed(range(len(rewards))):
            if i == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[i + 1]
            
            delta = rewards[i] + self.gamma * next_value * (1 - dones[i]) - values[i]
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[i]) * gae
            advantages.insert(0, gae)
            returns.insert(0, gae + values[i])
        
        return advantages, returns
    
    def train(self, episodes: int = 100) -> Dict[str, Any]:
        """Train policy using PPO."""
        logger.info(f"🎯 Starting PPO training for {episodes} episodes")
        
        for episode in range(episodes):
            state = self.env.reset()
            episode_reward = 0
            
            # Collect trajectory
            states = []
            actions = []
            rewards = []
            values = []
            log_probs = []
            dones = []
            
            for step in range(self.env.max_steps):
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                action, probs, value = self.policy.get_action_tensor(state_tensor)
                
                next_state, reward, done, info = self.env.step(action)
                
                states.append(state)
                actions.append(action)
                rewards.append(reward)
                values.append(value.item())
                log_probs.append(torch.log(probs[0, action]))
                dones.append(done)
                
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            # Compute advantages
            advantages, returns = self.compute_gae(rewards, values, dones)
            
            # Convert to tensors
            states_tensor = torch.FloatTensor(states)
            actions_tensor = torch.LongTensor(actions)
            returns_tensor = torch.FloatTensor(returns)
            advantages_tensor = torch.FloatTensor(advantages)
            old_log_probs_tensor = torch.stack(log_probs)
            
            # PPO update
            for epoch in range(self.ppo_epochs):
                # Random shuffle
                indices = torch.randperm(len(states))
                
                for start in range(0, len(states), self.batch_size):
                    end = start + self.batch_size
                    batch_indices = indices[start:end]
                    
                    batch_states = states_tensor[batch_indices]
                    batch_actions = actions_tensor[batch_indices]
                    batch_returns = returns_tensor[batch_indices]
                    batch_advantages = advantages_tensor[batch_indices]
                    batch_old_log_probs = old_log_probs_tensor[batch_indices]
                    
                    # Forward pass
                    logits, values_pred = self.policy(batch_states)
                    probs = F.softmax(logits, dim=-1)
                    new_log_probs = torch.log(probs.gather(1, batch_actions.unsqueeze(1)).squeeze())
                    
                    # Compute ratio
                    ratio = torch.exp(new_log_probs - batch_old_log_probs)
                    
                    # PPO loss
                    surr1 = ratio * batch_advantages
                    surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * batch_advantages
                    policy_loss = -torch.min(surr1, surr2).mean()
                    
                    # Value loss
                    value_loss = F.mse_loss(values_pred.squeeze(), batch_returns)
                    
                    # Entropy bonus
                    entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=-1).mean()
                    
                    # Total loss
                    loss = policy_loss + 0.5 * value_loss - self.entropy_bonus * entropy
                    
                    # Update
                    self.optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
                    self.optimizer.step()
                    
                    self.policy_losses.append(policy_loss.item())
                    self.value_losses.append(value_loss.item())
            
            self.episode_rewards.append(episode_reward)
            
            # Logging
            if episode % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_policy_loss = np.mean(self.policy_losses[-40:]) if self.policy_losses else 0
                avg_value_loss = np.mean(self.value_losses[-40:]) if self.value_losses else 0
                
                logger.info(f"Episode {episode}: Reward={avg_reward:.3f}, "
                           f"Policy Loss={avg_policy_loss:.4f}, Value Loss={avg_value_loss:.4f}")
        
        # Save final model
        self.policy.save_checkpoint("apex/models/policy_network.pt")
        
        return {
            "episodes": episodes,
            "final_reward": np.mean(self.episode_rewards[-10:]),
            "total_episodes": len(self.episode_rewards),
            "avg_policy_loss": np.mean(self.policy_losses),
            "avg_value_loss": np.mean(self.value_losses)
        }


class StrategyMutationEngine:
    """Genetic algorithm for strategy mutation and evolution."""
    
    def __init__(self):
        """Initialize mutation engine."""
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_ratio = 0.2
        
        # Historical best strategies
        self.best_historical = []
        
        logger.info("🧬 StrategyMutationEngine initialized")
    
    def mutate(self, current_params: Dict[str, Any], performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mutated strategy parameters."""
        mutated_params = current_params.copy()
        
        # Random perturbation
        for key, value in mutated_params.items():
            if isinstance(value, float) and np.random.random() < self.mutation_rate:
                perturbation = np.random.normal(0, 0.1)
                mutated_params[key] = np.clip(value + perturbation, 0.0, 1.0)
        
        # Crossover with best historical
        if self.best_historical and np.random.random() < self.crossover_rate:
            best_params = random.choice(self.best_historical)
            for key in mutated_params:
                if np.random.random() < 0.5:
                    mutated_params[key] = best_params.get(key, mutated_params[key])
        
        logger.debug("🧬 Mutation generated")
        return mutated_params
    
    def evaluate_mutation(self, params: Dict[str, Any], n_episodes: int = 20) -> float:
        """Evaluate mutated strategy parameters."""
        # Create environment with mutated parameters
        env = TradingEnvironment()
        
        # Simple evaluation (would use actual policy in production)
        total_sharpe = 0.0
        for episode in range(n_episodes):
            state = env.reset()
            episode_reward = 0
            
            for step in range(env.max_steps):
                # Simple policy based on parameters
                action = self._action_from_params(state, params)
                next_state, reward, done, info = env.step(action)
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            # Calculate Sharpe (simplified)
            total_sharpe += episode_reward / (0.1 + abs(episode_reward) * 0.1)
        
        avg_sharpe = total_sharpe / n_episodes
        logger.debug(f"📊 Mutation evaluation: Sharpe={avg_sharpe:.3f}")
        return avg_sharpe
    
    def _action_from_params(self, state: np.ndarray, params: Dict[str, Any]) -> int:
        """Simple action selection based on parameters."""
        # Weighted decision based on state and parameters
        weights = [
            params.get("price_momentum_weight", 0.2),
            params.get("sentiment_weight", 0.2),
            params.get("prism_weight", 0.2),
            params.get("volume_weight", 0.2),
            params.get("position_weight", 0.2)
        ]
        
        score = np.dot(state[:5], weights)
        
        if score > 0.1:
            return 1  # Buy
        elif score < -0.1:
            return 2  # Sell
        elif abs(state[5]) > 0.3:  # Large position
            return 3  # Close
        else:
            return 0  # Hold
    
    def apply_if_better(self, new_params: Dict[str, Any], current_sharpe: float) -> bool:
        """Apply new parameters if they improve performance."""
        new_sharpe = self.evaluate_mutation(new_params)
        
        improvement = (new_sharpe - current_sharpe) / current_sharpe if current_sharpe != 0 else 0
        
        if improvement >= 0.03:  # 3% improvement threshold
            self.best_historical.append(new_params)
            logger.info(f"✅ New parameters applied: {improvement:.2%} improvement")
            return True
        else:
            logger.info(f"❌ Parameters rejected: {improvement:.2%} improvement")
            return False


async def main():
    """Main execution function."""
    logger.info("🚀 Starting APEX RL System")
    
    try:
        # Create environment
        env = TradingEnvironment()
        
        # Train PPO
        trainer = PPOTrainer(env)
        results = trainer.train(episodes=10)
        
        print("\n" + "="*60)
        print("🧠 APEX REINFORCEMENT LEARNING RESULTS")
        print("="*60)
        print(f"🎯 Episodes: {results['episodes']}")
        print(f"📊 Final Reward: {results['final_reward']:.3f}")
        print(f"📈 Total Episodes: {results['total_episodes']}")
        print(f"🔧 Avg Policy Loss: {results['avg_policy_loss']:.4f}")
        print(f"📉 Avg Value Loss: {results['avg_value_loss']:.4f}")
        
        # Test mutation engine
        print("\n🧬 Testing Strategy Mutation:")
        mutation_engine = StrategyMutationEngine()
        current_params = {
            "price_momentum_weight": 0.3,
            "sentiment_weight": 0.2,
            "prism_weight": 0.3,
            "volume_weight": 0.1,
            "position_weight": 0.1
        }
        
        mutated = mutation_engine.mutate(current_params, {"sharpe": 0.5})
        print(f"📝 Mutated params: {mutated}")
        
        sharpe = mutation_engine.evaluate_mutation(mutated, n_episodes=5)
        print(f"📊 Mutation Sharpe: {sharpe:.3f}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"💥 RL system error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
