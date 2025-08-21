from PIL import Image
import os
import random

class PhotoAnalysisTools:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
    
    def analyze_damage_photo(self, file_path):
        """Analyze photo for damage with enhanced simulation"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": "Photo not found"}
            
            with Image.open(file_path) as img:
                width, height = img.size
                file_size = os.path.getsize(file_path)
                
                # damage checking
                damage_analysis = self._simulate_realistic_damage_analysis(file_path, width, height)
                
                return {
                    "success": True,
                    "analysis": {
                        "image_quality": "good" if width > 600 and height > 600 else "acceptable",
                        "dimensions": f"{width}x{height}",
                        "file_size_mb": round(file_size / (1024*1024), 2),
                        "damage_detected": damage_analysis["damage_found"],
                        "damage_severity": damage_analysis["severity"],
                        "confidence_score": damage_analysis["confidence"],
                        "analysis_notes": damage_analysis["notes"],
                        "recommendation": damage_analysis["recommendation"]
                    }
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_realistic_damage_analysis(self, file_path, width, height):
        """Enhanced damage simulation for RAG + RAT integration"""
        
        scenarios = [
            {
                "damage_found": True,
                "severity": "high", 
                "confidence": round(random.uniform(0.85, 0.95), 2),
                "notes": "Clear visible damage detected - product significantly damaged",
                "recommendation": "immediate_refund"
            },
            {
                "damage_found": True,
                "severity": "medium",
                "confidence": round(random.uniform(0.75, 0.85), 2), 
                "notes": "Moderate damage visible - functionality may be affected",
                "recommendation": "replacement_or_refund"
            },
            {
                "damage_found": True,
                "severity": "low",
                "confidence": round(random.uniform(0.65, 0.80), 2),
                "notes": "Minor damage detected - cosmetic issues visible",
                "recommendation": "replacement_preferred"
            },
            {
                "damage_found": False,
                "severity": "none",
                "confidence": round(random.uniform(0.70, 0.90), 2),
                "notes": "No significant damage visible - product appears intact",
                "recommendation": "further_investigation"
            }
        ]
        
        weights = [0.4, 0.3, 0.2, 0.1] 
        
        return random.choices(scenarios, weights=weights)[0]
    
    def validate_photo_upload(self, uploaded_file):
        """Enhanced photo validation"""
        validations = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # file size
        if uploaded_file.size > 10 * 1024 * 1024:
            validations["valid"] = False
            validations["errors"].append("File size too large (max 10MB)")
        
        # file type
        if uploaded_file.type not in ['image/jpeg', 'image/png', 'image/webp']:
            validations["valid"] = False
            validations["errors"].append("Invalid file type. Please upload JPG, PNG, or WebP")
        
        return validations
