import numpy as np
from typing import List, Dict, Any
from sklearn.metrics import cohen_kappa_score

def compute_inter_rater_agreement(rater1_labels: List[str], rater2_labels: List[str]) -> Dict[str, Any]:
    """
    Computes Cohen's Kappa between two raters (e.g. Officer vs. AI or Officer A vs. Officer B)
    to measure grading consistency and bias reduction.
    """
    if len(rater1_labels) == 0 or len(rater2_labels) == 0:
        return {"kappa": 0.0, "agreement_pct": 0.0, "interpretation": "Insufficient data"}
        
    kappa = cohen_kappa_score(rater1_labels, rater2_labels)
    agreement = np.mean([r1 == r2 for r1, r2 in zip(rater1_labels, rater2_labels)]) * 100.0
    
    # Landis & Koch (1977) Kappa interpretation standard
    if kappa < 0.20:
        interp = "Slight Agreement (High Human Discrepancy)"
    elif kappa < 0.40:
        interp = "Fair Agreement"
    elif kappa < 0.60:
        interp = "Moderate Agreement"
    elif kappa < 0.80:
        interp = "Substantial Agreement"
    else:
        interp = "Almost Perfect Agreement (High Objective Standard)"
        
    return {
        "kappa": round(float(kappa), 3),
        "agreement_pct": round(float(agreement), 1),
        "interpretation": interp
    }
