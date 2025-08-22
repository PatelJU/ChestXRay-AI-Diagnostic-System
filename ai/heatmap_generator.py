import torch
import numpy as np
from captum.attr import LayerGradCam, LayerAttribution
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import matplotlib
matplotlib.use('Agg')
import random

class HeatmapGenerator:
    def __init__(self, model):
        self.model = model
        self.target_layer = self.model.features.denseblock4.denselayer16.conv2
        self.colormap = cv2.COLORMAP_JET
        self.resolution_factor = 16  # Increased for more detail
        self.blur_factor = 5  # Reduced blur for more localized medical visualization

    def generate_heatmap(self, input_tensor, target_idx):
        """Generate smooth Grad-CAM heatmap for a specific target"""
        from captum.attr import LayerGradCam, LayerAttribution
        gradcam = LayerGradCam(self.model, self.target_layer)
        attributions = gradcam.attribute(input_tensor, target=target_idx)
        upsampled = LayerAttribution.interpolate(attributions, (224, 224), interpolate_mode='bicubic')
        heatmap = upsampled[0, 0].detach().cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1
        # Apply stronger Gaussian blur for smooth, curved edges
        heatmap = cv2.GaussianBlur(heatmap, (self.blur_factor, self.blur_factor), 0)
        return heatmap

    def generate_all_heatmaps(self, input_tensor, predictions, pathologies):
        """Generate heatmaps for all diseases, sorted by probability"""
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        heatmaps = {}
        for disease, prob in sorted_preds:
            try:
                target_idx = pathologies.index(disease)
                if 0 <= target_idx < len(self.model.pathologies):
                    heatmaps[disease] = self.generate_heatmap(input_tensor, target_idx)
            except ValueError:
                continue
        return heatmaps, [disease for disease, _ in sorted_preds]

    def create_combined_heatmap(self, original_img, heatmaps, predictions):
        """Create weighted average combined heatmap"""
        if not heatmaps:
            return original_img.copy()
        
        # Initialize averaged heatmap
        avg_heatmap = np.zeros((224, 224), dtype=np.float32)
        total_weight = 0
        
        for disease, hmap in heatmaps.items():
            weight = predictions.get(disease, 0)
            avg_heatmap += hmap * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_heatmap /= total_weight
        
        # Smooth the averaged heatmap
        avg_heatmap = cv2.GaussianBlur(avg_heatmap, (self.blur_factor, self.blur_factor), 0)
        
        return self.overlay_heatmap(original_img, avg_heatmap)

    def overlay_heatmap(self, original_img, heatmap, alpha=0.5):
        """Overlay smooth heatmap on original image"""
        high_res_shape = (original_img.shape[1] * self.resolution_factor, 
                         original_img.shape[0] * self.resolution_factor)
        
        original_hr = cv2.resize(original_img, high_res_shape, interpolation=cv2.INTER_CUBIC)
        heatmap_hr = cv2.resize(heatmap, high_res_shape, interpolation=cv2.INTER_CUBIC)
        
        heatmap_hr = np.uint8(255 * heatmap_hr)
        colored = cv2.applyColorMap(heatmap_hr, self.colormap)
        
        overlay = cv2.addWeighted(original_hr, 1 - alpha, colored, alpha, 0)
        
        return cv2.resize(overlay, (original_img.shape[1], original_img.shape[0]), interpolation=cv2.INTER_AREA)

    def get_individual_overlay(self, original_img, disease, heatmaps):
        """Get overlay for specific disease"""
        if disease not in heatmaps:
            return original_img.copy()
        return self.overlay_heatmap(original_img, heatmaps[disease])

    def get_circle_overlay(self, original_img, disease, heatmaps):
        """Get circle overlay for specific disease"""
        if disease not in heatmaps:
            return original_img.copy()
        return self.generate_circle_overlay(original_img, disease, heatmaps[disease])

    def create_multi_circle_overlay(self, original_img, heatmaps, predictions, max_circles=3):
        """Create overlay with multiple circles for top diseases"""
        if not heatmaps:
            return original_img.copy()
        
        # Sort diseases by probability
        sorted_diseases = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        
        # Start with original image
        result = original_img.copy()
        
        # Add circles for top diseases
        for i, (disease, prob) in enumerate(sorted_diseases):
            if i >= max_circles or prob < 0.1:  # Only show top diseases with significant probability
                break
            if disease in heatmaps:
                # Generate circle overlay for this disease
                circle_overlay = self.generate_circle_overlay(result, disease, heatmaps[disease])
                # Add text label near the circle
                y, x = np.unravel_index(np.argmax(heatmaps[disease]), heatmaps[disease].shape)
                text_pos = (int(x * result.shape[1] / heatmaps[disease].shape[1]), 
                           int(y * result.shape[0] / heatmaps[disease].shape[0] - 20))  # 20px above circle
                cv2.putText(circle_overlay, f"{disease}: {prob*100:.1f}%", text_pos, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                result = circle_overlay
        
        return result

    def generate_circle_overlay(self, original_img, disease, heatmap):
        if heatmap is None:
            return original_img.copy()
        
        # Find center of highest intensity
        y, x = np.unravel_index(np.argmax(heatmap), heatmap.shape)
        center = (int(x * original_img.shape[1] / heatmap.shape[1]), int(y * original_img.shape[0] / heatmap.shape[0]))
        radius = int(min(original_img.shape[:2]) * 0.15)  # 15% of smaller dimension
        
        # Disease-specific colors (BGR, semi-transparent)
        colors = {
            'Pneumonia': (0, 0, 255, 128),  # Red
            'Tuberculosis': (0, 255, 255, 128),  # Yellow
            'COVID': (0, 165, 255, 128),  # Orange
            'Atelectasis': (255, 0, 0, 128),  # Blue
            'Cardiomegaly': (0, 255, 0, 128),  # Green
            'Pneumothorax': (255, 0, 255, 128),  # Magenta
            # Add more as needed
        }
        color = colors.get(disease, (random.randint(0,255), random.randint(0,255), random.randint(0,255), 128))
        
        overlay = original_img.copy()
        cv2.circle(overlay, center, radius, color[:3], -1)  # Filled circle
        
        # Blend with alpha
        alpha = color[3] / 255.0
        result = cv2.addWeighted(overlay, alpha, original_img, 1 - alpha, 0)
        
        return result