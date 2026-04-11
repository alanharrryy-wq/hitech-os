# qa_benchmark_suite

- fix_success_rate: 0.333
- degraded_rate: 0.333
- false_fix_rate: 0.333
- avg_time_to_first_useful_hypothesis_ms: 63.160

## scenarios

- `batch_positive_control` [fix] success=True applied=True degraded=False false_fix=False duration_ms=156.916
- `large_file_positive_control` [fix] success=False applied=True degraded=False false_fix=False duration_ms=154.302
- `false_fix_negative_control` [fix] success=False applied=True degraded=True false_fix=True duration_ms=11.984
- `diagnostic_python_case` [diagnostic] success=True applied=False degraded=False false_fix=False duration_ms=158.302
- `diagnostic_node_case` [diagnostic] success=True applied=False degraded=False false_fix=False duration_ms=16.231
- `diagnostic_web_case` [diagnostic] success=True applied=False degraded=False false_fix=False duration_ms=14.947
