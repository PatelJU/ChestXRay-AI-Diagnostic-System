import datetime

class ReportGenerator:
    def __init__(self):
        self.disease_descriptions = {
            'Atelectasis': 'Partial or complete collapse of the lung, often due to blockage or pressure.',
            'Consolidation': 'Filling of lung airspaces with fluid, often seen in pneumonia.',
            'Infiltration': 'Abnormal substances in lung tissue, possibly indicating infection or inflammation.',
            'Pneumothorax': 'Collapsed lung due to air in the pleural space.',
            'Edema': 'Fluid accumulation in lung tissue, often related to heart conditions.',
            'Emphysema': 'Destruction of lung tissue leading to air trapping.',
            'Fibrosis': 'Scarring of lung tissue, reducing lung function.',
            'Effusion': 'Fluid buildup in the pleural space.',
            'Pneumonia': 'Infection causing lung inflammation and fluid buildup.',
            'Pleural Thickening': 'Thickening of the lung lining, often from inflammation or scarring.',
            'Cardiomegaly': 'Enlarged heart, potentially indicating heart disease.',
            'Nodule': 'Small abnormal growth in the lung.',
            'Mass': 'Larger abnormal growth in the lung.',
            'Hernia': 'Protrusion of abdominal contents into the chest.',
            'Lung Lesion': 'Abnormal area in the lung tissue.',
            'Fracture': 'Bone break, possibly rib or clavicle.',
            'Lung Tumor': 'Abnormal growth in lung, potentially cancerous.',
            'Enlarged Cardiomediastinum': 'Widening of the central chest area, possibly due to vascular issues.',
            # Add dataset-specific diseases
            'COVID': 'Viral infection causing ground-glass opacities and consolidations.',
            'Lung_Opacity': 'Areas of increased density in the lung, various causes.',
            'Tuberculosis': 'Bacterial infection often causing cavities and infiltrates.',
            'Normal': 'No abnormalities detected.'
        }
        self.urgency_levels = {
            'Pneumonia': 'High - Seek emergency care if breathing difficulties present',
            'Tuberculosis': 'Medium - Prompt medical evaluation recommended',
            'COVID': 'High - Immediate isolation and testing advised',
            'Atelectasis': 'Medium - Follow up with physician',
            'Cardiomegaly': 'Medium - Cardiac evaluation recommended',
            'Pneumothorax': 'High - Emergency medical attention required',
            # Add more as needed
        }
        self.recommendations = {
            'high': 'Immediate medical attention recommended. Consult a physician urgently.',
            'medium': 'Follow-up with a healthcare provider is advised.',
            'low': 'Monitor symptoms and consult if changes occur.'
        }

    def generate_summary(self, predictions):
        top_diseases = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:5]
        summary = "Executive Summary:\n"
        for disease, prob in top_diseases:
            if prob > 0.1:
                # Clean description to avoid any HTML issues
                desc = self.disease_descriptions.get(disease, 'Description not available')
                # Remove any potential HTML-like characters that might cause issues
                desc = desc.replace('<', '').replace('>', '').replace('&', 'and')
                summary += f"- {disease} ({prob*100:.1f}% probability): {desc}\n"
        return summary

    def generate_detailed_report(self, predictions):
        report = f"Comprehensive Chest X-Ray Analysis Report\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "1. Overview\n"
        report += "This report provides AI-assisted analysis of the chest X-ray using pre-trained deep learning models. "
        report += "Probabilities indicate likelihood of detected pathologies. All findings should be verified by a qualified radiologist.\n\n"
        
        report += "2. Detailed Probability Analysis\n"
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_preds:
            if prob > 0.05:  # Include only significant probabilities
                risk_level = 'high' if prob > 0.7 else 'medium' if prob > 0.3 else 'low'
                report += f"- {disease}: {prob*100:.2f}%\n"
                report += f"  Description: {self.disease_descriptions.get(disease, 'No description available')}\n"
                report += f"  Risk Level: {risk_level.capitalize()}\n"
                urgency = self.urgency_levels.get(disease, 'Consult a medical professional')
                report += f"  Urgency: {urgency}\n"
                report += f"  Recommendation: {self.recommendations.get(risk_level, 'Consult a medical professional')}\n\n"
        
        report += "3. Interpretation Notes\n"
        top_disease = sorted_preds[0][0] if sorted_preds else 'Normal'
        report += f"- Primary finding: {top_disease}\n"
        report += f"- {self.urgency_levels.get(top_disease, 'Standard monitoring recommended')}\n"
        report += "- Probabilities above 50% indicate strong likelihood and warrant attention.\n"
        report += "- Multiple findings may indicate complex conditions.\n"
        report += "- Always correlate with clinical symptoms.\n\n"
        
        report += "4. Limitations\n"
        report += "This AI analysis is based on pre-trained models and may not detect all conditions, "
        report += "especially rare or subtle abnormalities. Not a substitute for professional medical advice.\n"
        
        return report