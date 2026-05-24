# Machine Learning Model Comparison

This document compares 5 different machine learning architectures on the Smart Home Threat Simulation dataset.

> **Note on SVM:** Due to the massive dataset size (1.6M rows), training a standard kernel `SVC` would have taken an unfeasible amount of time (time complexity $O(n^2)$). We explicitly utilized **`LinearSVC`** to test a highly-optimized margin-based classifier capable of handling large-scale tabular data.

## Performance Metrics

| Model | Accuracy | Precision | Recall | F1-Score | Training Time (s) | Comment |
|---|---|---|---|---|---|---|
| **Random Forest** | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 37.1s | Strong ensemble baseline (Current Prod) |
| **Decision Tree** | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 4.6s | Simple, highly interpretable rule-based tree |
| **LinearSVC** | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 19.4s | Scalable margin-based classifier (Linear approx) |
| **XGBoost** | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 15.6s | State-of-the-art gradient boosting framework |
| **Logistic Regression** | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 4.0s | Traditional linear baseline model |

## Conclusion
*(Auto-generated results. Review the table above for insights into model selection vs compute trade-offs.)*
