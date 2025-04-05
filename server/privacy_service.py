import numpy as np
import logging
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PrivacyService:
    def __init__(self):
        """Initialize the privacy service."""
        pass
    
    def add_noise_to_weights(self, weights, epsilon=2.0, delta=1e-5):
        """
        Add differential privacy noise to model weights.
        
        Args:
            weights (dict): Dictionary of model weights.
            epsilon (float): Privacy parameter (smaller = more privacy).
            delta (float): Failure probability parameter.
            
        Returns:
            dict: Dictionary of privatized weights.
        """
        try:
            # Create a copy of the weights to avoid modifying the original
            private_weights = {}
            
            # Calculate the sensitivity (largest possible change from a single training example)
            # This is a simplification; in practice, this would be calculated based on clipping norm
            sensitivity = 1.0
            
            # Calculate noise scale based on epsilon and delta (Gaussian mechanism)
            noise_scale = self._calculate_noise_scale(epsilon, delta, sensitivity)
            
            logger.info(f"Adding noise with scale {noise_scale} (epsilon={epsilon}, delta={delta})")
            
            # Add noise to each weight tensor
            for key, value in weights.items():
                if isinstance(value, list):
                    # If the weight is already a list (numpy array was converted to list)
                    weight_array = np.array(value)
                    noise = np.random.normal(0, noise_scale, weight_array.shape)
                    private_weights[key] = (weight_array + noise).tolist()
                elif isinstance(value, np.ndarray):
                    # If the weight is a numpy array
                    noise = np.random.normal(0, noise_scale, value.shape)
                    private_weights[key] = (value + noise).tolist()
                elif isinstance(value, torch.Tensor):
                    # If the weight is a torch tensor
                    tensor_shape = value.shape
                    noise = torch.normal(0, noise_scale, tensor_shape)
                    private_weights[key] = (value + noise).cpu().numpy().tolist()
                else:
                    # For other types, pass through unchanged
                    private_weights[key] = value
            
            return private_weights
            
        except Exception as e:
            logger.error(f"Error applying differential privacy: {str(e)}")
            raise
    
    def _calculate_noise_scale(self, epsilon, delta, sensitivity):
        """
        Calculate the scale of Gaussian noise to add for differential privacy.
        
        Uses the Gaussian mechanism with advanced composition theorem.
        
        Args:
            epsilon (float): Privacy parameter.
            delta (float): Failure probability.
            sensitivity (float): Sensitivity of the query.
            
        Returns:
            float: Scale of the noise to add.
        """
        # Gaussian mechanism noise scale calculation
        # Based on the analytic Gaussian mechanism for (ε,δ)-DP
        c = np.sqrt(2 * np.log(1.25 / delta))
        noise_scale = sensitivity * c / epsilon
        
        return noise_scale
    
    def privatize_gradients(self, gradients, epsilon=2.0, delta=1e-5, clip_norm=1.0):
        """
        Apply differential privacy to gradients using gradient clipping and noise addition.
        
        Args:
            gradients (dict): Dictionary of gradients.
            epsilon (float): Privacy parameter.
            delta (float): Failure probability.
            clip_norm (float): Maximum L2 norm for gradient clipping.
            
        Returns:
            dict: Dictionary of privatized gradients.
        """
        try:
            # Clone the gradients
            private_gradients = {}
            
            # First, clip the gradients
            clipped_gradients = self._clip_gradients(gradients, clip_norm)
            
            # Calculate the sensitivity based on the clipping norm
            sensitivity = clip_norm
            
            # Calculate noise scale
            noise_scale = self._calculate_noise_scale(epsilon, delta, sensitivity)
            
            # Add noise to each gradient
            for key, value in clipped_gradients.items():
                if isinstance(value, list):
                    # If the gradient is already a list
                    grad_array = np.array(value)
                    noise = np.random.normal(0, noise_scale, grad_array.shape)
                    private_gradients[key] = (grad_array + noise).tolist()
                elif isinstance(value, np.ndarray):
                    # If the gradient is a numpy array
                    noise = np.random.normal(0, noise_scale, value.shape)
                    private_gradients[key] = (value + noise).tolist()
                elif isinstance(value, torch.Tensor):
                    # If the gradient is a torch tensor
                    tensor_shape = value.shape
                    noise = torch.normal(0, noise_scale, tensor_shape)
                    private_gradients[key] = (value + noise).cpu().numpy().tolist()
                else:
                    # For other types, pass through unchanged
                    private_gradients[key] = value
            
            return private_gradients
            
        except Exception as e:
            logger.error(f"Error privatizing gradients: {str(e)}")
            raise
    
    def _clip_gradients(self, gradients, clip_norm):
        """
        Clip gradients to have a maximum L2 norm.
        
        Args:
            gradients (dict): Dictionary of gradients.
            clip_norm (float): Maximum L2 norm.
            
        Returns:
            dict: Dictionary of clipped gradients.
        """
        try:
            # Clone the gradients
            clipped_gradients = {}
            
            for key, value in gradients.items():
                if isinstance(value, list):
                    # If the gradient is already a list
                    grad_array = np.array(value)
                    grad_norm = np.linalg.norm(grad_array)
                    
                    if grad_norm > clip_norm:
                        grad_array = grad_array * (clip_norm / grad_norm)
                    
                    clipped_gradients[key] = grad_array.tolist()
                elif isinstance(value, np.ndarray):
                    # If the gradient is a numpy array
                    grad_norm = np.linalg.norm(value)
                    
                    if grad_norm > clip_norm:
                        clipped_gradients[key] = value * (clip_norm / grad_norm)
                    else:
                        clipped_gradients[key] = value
                elif isinstance(value, torch.Tensor):
                    # If the gradient is a torch tensor
                    grad_norm = torch.norm(value)
                    
                    if grad_norm > clip_norm:
                        clipped_gradients[key] = (value * (clip_norm / grad_norm)).cpu().numpy()
                    else:
                        clipped_gradients[key] = value.cpu().numpy()
                else:
                    # For other types, pass through unchanged
                    clipped_gradients[key] = value
            
            return clipped_gradients
            
        except Exception as e:
            logger.error(f"Error clipping gradients: {str(e)}")
            raise
