-- Minimal provenance-aware evidence schema (DuckDB dialect).
-- Principles:
--   * a claim is an addressable record with its own provenance, never a bare fact;
--   * record_origin (what kind of thing the record is) and epistemic_status
--     (how far we trust it) are separate columns;
--   * review_status records HOW the project accessed the claim (direct,
--     via a secondary source, via machine summary) and is not a reliability score;
--   * synthetic and simulated records cannot enter these tables: they live in
--     model outputs with record_origin in ('synthetic','simulated').

CREATE TYPE IF NOT EXISTS access_status AS ENUM (
  'inspected_full_text', 'inspected_partial', 'machine_summary_only',
  'metadata_only', 'cited_only', 'unavailable');

CREATE TYPE IF NOT EXISTS record_origin AS ENUM (
  'transcribed_reading', 'literary_statement', 'archaeological_observation',
  'scholarly_reconstruction', 'project_derivation', 'synthetic', 'simulated');

CREATE TYPE IF NOT EXISTS epistemic_status AS ENUM (
  'accepted_working', 'uncertain', 'disputed', 'unresolved', 'rhetorical', 'rejected');

CREATE TYPE IF NOT EXISTS review_status AS ENUM (
  'inspected', 'inspected_in_secondary', 'machine_summary_only', 'cited_only', 'human_reviewed');

CREATE TABLE IF NOT EXISTS rights (
  rights_id VARCHAR PRIMARY KEY,
  license_or_terms VARCHAR,
  private_research_use VARCHAR,
  tdm_permitted VARCHAR,
  redistribute_full_text VARCHAR,
  redistribute_derived_data VARCHAR,
  checked_on VARCHAR,
  evidence VARCHAR);

CREATE TABLE IF NOT EXISTS source (
  source_id VARCHAR PRIMARY KEY,
  kind VARCHAR NOT NULL,          -- work | edition | chapter | article | dataset | file_copy | reading | web_page | thesis | working_paper
  creators VARCHAR,
  year VARCHAR,                   -- text: cited years can disagree (see SRC-RATHBONE-2000)
  title VARCHAR,
  container_or_series VARCHAR,
  identifiers VARCHAR,
  access_status access_status NOT NULL,
  rights_id VARCHAR REFERENCES rights(rights_id),
  cited_via VARCHAR);

CREATE TABLE IF NOT EXISTS document (   -- ancient object / text / archive
  document_id VARCHAR PRIMARY KEY,
  designation VARCHAR NOT NULL,
  aliases VARCHAR,
  kind VARCHAR,
  date_low_ce INTEGER,
  date_high_ce INTEGER,
  place VARCHAR,
  edition_inspected VARCHAR);

CREATE TABLE IF NOT EXISTS assertion (
  assertion_id VARCHAR PRIMARY KEY,
  document_id VARCHAR REFERENCES document(document_id),   -- NULL for purely modern calculations
  locus VARCHAR,                  -- ancient locus (col./line, book.chapter)
  quantity_concept VARCHAR,
  value_low DOUBLE,
  value_high DOUBLE,
  unit VARCHAR,
  claim_text VARCHAR,
  asserted_by VARCHAR,            -- source_id of the reader / interpreter
  reported_in VARCHAR REFERENCES source(source_id),
  page VARCHAR,                   -- modern page, only if verified
  record_origin record_origin NOT NULL,
  epistemic_status epistemic_status NOT NULL,
  review_status review_status NOT NULL,
  CHECK (record_origin NOT IN ('synthetic', 'simulated')));

CREATE TABLE IF NOT EXISTS parameter (
  param_id VARCHAR PRIMARY KEY,
  definition VARCHAR,
  unit VARCHAR,
  baseline DOUBLE,
  low DOUBLE,
  high DOUBLE,
  status VARCHAR CHECK (status IN ('measured_input','external_estimate','calibrated','exploratory')));

-- Typed edges: parameter -> assertion (derived_from); assertion -> assertion (depends_on);
-- source -> source (cites). Kept generic so recursive lineage queries are one CTE.
CREATE TABLE IF NOT EXISTS dependency (
  from_id VARCHAR NOT NULL,
  to_id VARCHAR NOT NULL,
  relation VARCHAR NOT NULL CHECK (relation IN ('derived_from','depends_on','cites','about')),
  PRIMARY KEY (from_id, to_id, relation));

CREATE TABLE IF NOT EXISTS conversion_rule (
  rule_id VARCHAR PRIMARY KEY,
  from_unit VARCHAR, to_unit VARCHAR, factor DOUBLE,
  scope VARCHAR, source_id VARCHAR, locus VARCHAR, status VARCHAR, note VARCHAR);
