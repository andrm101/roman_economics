-- name: CQ1_params_depending_on_document
-- Which model parameters ultimately depend on a given ancient document?
-- (bind :doc via string replacement in romeco.evidence_db)
WITH RECURSIVE lineage(param_id, node) AS (
  SELECT from_id, to_id FROM dependency
  WHERE relation = 'derived_from'
  UNION
  SELECT l.param_id, d.to_id FROM lineage l
  JOIN dependency d ON d.from_id = l.node AND d.relation = 'depends_on'
)
SELECT DISTINCT l.param_id
FROM lineage l JOIN assertion a ON a.assertion_id = l.node
WHERE a.document_id = '{doc}'
ORDER BY 1;

-- name: CQ2_params_resting_on_unverified_access
-- Which parameters rest on claims the project has not inspected directly?
SELECT d.from_id AS param_id, a.assertion_id, a.review_status, a.epistemic_status
FROM dependency d JOIN assertion a ON a.assertion_id = d.to_id
WHERE d.relation = 'derived_from'
  AND a.review_status IN ('machine_summary_only', 'cited_only')
ORDER BY 1, 2;

-- name: CQ3_unique_primary_documents_per_parameter
-- How many distinct primary documents underlie each parameter? (independence check)
SELECT p.param_id, p.status,
       count(DISTINCT a.document_id) AS n_primary_documents,
       count(DISTINCT a.assertion_id) AS n_assertions,
       string_agg(DISTINCT a.document_id, '; ') AS documents
FROM parameter p
LEFT JOIN dependency d ON d.from_id = p.param_id AND d.relation = 'derived_from'
LEFT JOIN assertion a ON a.assertion_id = d.to_id
GROUP BY 1, 2 ORDER BY 3 DESC, 1;

-- name: CQ4_critical_sources_not_inspected
-- Sources that report claims feeding parameters but were never inspected.
SELECT DISTINCT s.source_id, s.access_status, s.title
FROM dependency d
JOIN assertion a ON a.assertion_id = d.to_id
JOIN source s ON s.source_id IN (a.asserted_by, a.reported_in)
WHERE d.relation = 'derived_from'
  AND s.access_status NOT IN ('inspected_full_text', 'inspected_partial')
ORDER BY 1;

-- name: CQ5_contested_inputs
-- Disputed / unresolved / rhetorical claims that feed parameters.
SELECT d.from_id AS param_id, a.assertion_id, a.epistemic_status, a.claim_text
FROM dependency d JOIN assertion a ON a.assertion_id = d.to_id
WHERE d.relation = 'derived_from'
  AND a.epistemic_status IN ('disputed', 'unresolved', 'rhetorical')
ORDER BY 1, 2;
