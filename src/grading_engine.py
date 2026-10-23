import numpy as np
from typing import List, Dict, Any, Tuple
from src.config import DEFAULT_GRADING_CONFIG

class MandiGradingEngine:
    """
    Deterministic & Configurable Procurement Grading Rules Engine.
    Implements 2026 Procurement Norms, URS specifications, and statistical confidence intervals.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = DEFAULT_GRADING_CONFIG.copy()
        if config:
            self.config.update(config)

    def grade_single_bulb(
        self,
        predicted_class: str,       # 'GOOD' or 'BAD'
        confidence: float,          # Classification confidence (0.0 to 1.0)
        diameter_mm: float,         # Measured equatorial diameter in mm
        blemish_pct: float = 0.0    # Surface blemish percentage
    ) -> Dict[str, Any]:
        """
        Grades an individual onion bulb based on multi-criteria rules:
        - Visual quality (Rotten / Sprouted / Damaged / Clean)
        - Physical diameter bounds
        - Surface blemish tolerance
        """
        cfg = self.config
        reasons = []
        
        is_visually_good = (predicted_class.upper() == "GOOD")
        
        # Check visual defects
        if not is_visually_good:
            reasons.append("Visual defect detected (Rot/Sprout/Damage)")
            
        # Check size criteria
        is_grade_a_size = (cfg["grade_a_min_diameter_mm"] <= diameter_mm <= cfg["grade_a_max_diameter_mm"])
        is_urs_size = (cfg["urs_min_diameter_mm"] <= diameter_mm <= cfg["urs_max_diameter_mm"])
        
        if not is_grade_a_size:
            if diameter_mm < cfg["grade_a_min_diameter_mm"]:
                reasons.append(f"Undersized ({diameter_mm:.1f} mm < {cfg['grade_a_min_diameter_mm']} mm)")
            else:
                reasons.append(f"Oversized ({diameter_mm:.1f} mm > {cfg['grade_a_max_diameter_mm']} mm)")
                
        # Check blemish tolerance
        is_grade_a_blemish = (blemish_pct <= cfg["max_allowed_blemish_pct"])
        is_urs_blemish = (blemish_pct <= cfg["urs_max_blemish_pct"])
        
        if not is_grade_a_blemish:
            reasons.append(f"Surface blemish {blemish_pct:.1f}% exceeds Grade A limit ({cfg['max_allowed_blemish_pct']}%)")
            
        # Decision Logic
        if is_visually_good and is_grade_a_size and is_grade_a_blemish:
            grade = "Grade A"
            status = "ACCEPTED"
            reason_str = "Meets all Grade A standards"
        elif cfg.get("enable_urs", True) and is_visually_good and is_urs_size and is_urs_blemish:
            grade = "URS"
            status = "RELAXED"
            reason_str = f"Qualified under URS: {', '.join(reasons)}"
        else:
            grade = "REJECTED"
            status = "REJECTED"
            reason_str = f"Rejection reasons: {', '.join(reasons)}"
            
        return {
            "grade": grade,
            "status": status,
            "predicted_class": predicted_class,
            "confidence": round(confidence, 3),
            "diameter_mm": round(diameter_mm, 1),
            "blemish_pct": round(blemish_pct, 1),
            "reasons": reason_str
        }

    @staticmethod
    def calculate_wilson_ci(count: int, total: int, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculates Wilson Score Confidence Interval for proportions.
        Returns: (proportion_pct, ci_lower_pct, ci_upper_pct)
        """
        if total == 0:
            return 0.0, 0.0, 0.0
            
        p = count / total
        z = 1.96 if confidence >= 0.95 else 1.645 # standard normal quantile for 95%
        
        denominator = 1.0 + (z ** 2) / total
        centre_adjusted_probability = p + (z ** 2) / (2.0 * total)
        adjusted_std_dev = np.sqrt((p * (1.0 - p) + (z ** 2) / (4.0 * total)) / total)
        
        lower_bound = max(0.0, (centre_adjusted_probability - z * adjusted_std_dev) / denominator)
        upper_bound = min(1.0, (centre_adjusted_probability + z * adjusted_std_dev) / denominator)
        
        return round(p * 100.0, 1), round(lower_bound * 100.0, 1), round(upper_bound * 100.0, 1)

    def evaluate_batch(self, graded_bulbs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates individual bulb grades into batch statistics with Wilson 95% CI.
        """
        total = len(graded_bulbs)
        if total == 0:
            return {
                "total_bulbs": 0,
                "grade_a": {"count": 0, "pct": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
                "urs": {"count": 0, "pct": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
                "rejected": {"count": 0, "pct": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
                "avg_diameter_mm": 0.0,
                "batch_verdict": "NO_BULBS_DETECTED"
            }
            
        grade_a_count = sum(1 for b in graded_bulbs if b["grade"] == "Grade A")
        urs_count = sum(1 for b in graded_bulbs if b["grade"] == "URS")
        rej_count = sum(1 for b in graded_bulbs if b["grade"] == "REJECTED")
        
        conf = self.config.get("confidence_level", 0.95)
        a_pct, a_low, a_high = self.calculate_wilson_ci(grade_a_count, total, conf)
        urs_pct, urs_low, urs_high = self.calculate_wilson_ci(urs_count, total, conf)
        rej_pct, rej_low, rej_high = self.calculate_wilson_ci(rej_count, total, conf)
        
        avg_diam = float(np.mean([b["diameter_mm"] for b in graded_bulbs]))
        
        # Batch Overall Mandi Recommendation
        if a_pct >= 70.0:
            verdict = "PASSED_GRADE_A (Procurement Approved at Full MSP)"
        elif (a_pct + urs_pct) >= 65.0:
            verdict = "PASSED_URS (Procurement Approved under Relaxed Norms)"
        else:
            verdict = "BATCH_REJECTED (High Defect / Size Non-compliance)"
            
        return {
            "total_bulbs": total,
            "grade_a": {"count": grade_a_count, "pct": a_pct, "ci_lower": a_low, "ci_upper": a_high},
            "urs": {"count": urs_count, "pct": urs_pct, "ci_lower": urs_low, "ci_upper": urs_high},
            "rejected": {"count": rej_count, "pct": rej_pct, "ci_lower": rej_low, "ci_upper": rej_high},
            "avg_diameter_mm": round(avg_diam, 1),
            "batch_verdict": verdict,
            "graded_bulbs": graded_bulbs
        }
