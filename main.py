"""
ChestXRay AI Diagnostic System

An advanced medical imaging analysis application that uses pre-trained deep learning models
to detect various chest conditions from X-ray images. The system provides:
- Multi-disease detection with confidence scores
- Visual heatmap analysis highlighting areas of concern
- Comprehensive medical reports with emergency alerts
- Professional PDF report generation

Author: Medical AI Research Team
Version: 1.0.0
"""

import tkinter as tk
from gui.main_window import MainWindow
from ai.model_manager import ModelManager
from ai.report_generator import ReportGenerator
from ai.heatmap_generator import HeatmapGenerator
from ai.medical_report_generator import MedicalReportGenerator
import torch
import torchxrayvision as xrv
import numpy as np
import skimage
from PIL import Image
import cv2

class MedicalAIApp:
    """
    Main application class for the ChestXRay AI Diagnostic System.
    
    This class orchestrates the entire application, managing:
    - GUI initialization and display
    - Model loading and management
    - Image analysis pipeline
    - Report generation
    - Heatmap visualization
    """
    
    def __init__(self):
        """Initialize the application with all necessary components."""
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("ChestXRay AI Diagnostic System")
        self.root.geometry("1200x800")
        self.model_manager = ModelManager()
        self.report_generator = ReportGenerator()
        self.heatmap_generator = HeatmapGenerator(self.model_manager.model)
        self.pdf_generator = MedicalReportGenerator()  # New professional PDF generator
        self.main_window = MainWindow(self.root, self)

    def analyze(self, img_path):
        """
        Perform comprehensive analysis on a chest X-ray image.
        
        Args:
            img_path (str): Path to the X-ray image file
        
        Returns:
            tuple: Contains predictions, summary, detailed report, and heatmap data
                - predictions (dict): Disease probabilities
                - summary (str): Brief analysis summary
                - report (str): Detailed medical report
                - heatmap_data (dict): Visualization data including heatmaps
        """
        # Get predictions from model
        predictions = self.model_manager.predict(img_path)
        
        # Generate text reports
        summary = self.report_generator.generate_summary(predictions)
        report = self.report_generator.generate_detailed_report(predictions)
        
        # Prepare input for heatmap generation
        img = skimage.io.imread(img_path)
        img = xrv.datasets.normalize(img, 255)
        if img.ndim == 3:
            img = img.mean(2)
        img = img[None, :, :]
        from skimage.transform import resize
        img = resize(img, (1, 224, 224), mode='constant')
        input_tensor = torch.from_numpy(img).float().unsqueeze(0)
        
        # Read original image for visualization
        original_img = cv2.imread(img_path)
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        
        # Generate all disease heatmaps and sorted list
        heatmaps, sorted_diseases = self.heatmap_generator.generate_all_heatmaps(
            input_tensor, predictions, self.model_manager.pathologies)
        
        # Create combined weighted average heatmap
        combined_overlay = self.heatmap_generator.create_combined_heatmap(
            original_img, heatmaps, predictions)
        
        # Return generated items
        return predictions, summary, report, {
            'combined': combined_overlay,
            'heatmaps': heatmaps,
            'sorted_diseases': sorted_diseases,
            'original_img': original_img
        }

    def run(self):
        """Launch the application GUI and start the main event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = MedicalAIApp()
    app.run()