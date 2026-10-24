import duckdb
import pytest

from romeco.evidence_db import build, dangling_evidence, run_query


@pytest.fixture(scope="module")
def con():
    return build()


def test_no_dangling_parameter_evidence(con):
    assert dangling_evidence(con) == []


def test_cq1_params_depending_on_muziris_papyrus(con):
    df = run_query(con, "CQ1_params_depending_on_document", doc="DOC-PVINDOB-G40822")
    assert set(df.param_id) == {"A_H", "tau"}


def test_cq3_flags_single_document_parameters(con):
    df = run_query(con, "CQ3_unique_primary_documents_per_parameter").set_index("param_id")
    assert df.loc["A_H", "n_primary_documents"] == 1
    assert df.loc["lam", "n_primary_documents"] == 0   # no evidence at all: exploratory


def test_synthetic_records_cannot_enter_evidence_tables(con):
    with pytest.raises(duckdb.ConstraintException):
        con.execute("INSERT INTO assertion (assertion_id, record_origin, epistemic_status, review_status) "
                    "VALUES ('X-SYN', 'synthetic', 'uncertain', 'inspected')")


def test_unverified_access_is_visible(con):
    df = run_query(con, "CQ2_params_resting_on_unverified_access")
    assert "RD-HERM-TOTAL-MORELLI" in set(df.assertion_id)


def test_every_source_has_known_rights(con):
    n = con.execute("SELECT count(*) FROM source WHERE rights_id NOT IN (SELECT rights_id FROM rights)").fetchone()[0]
    assert n == 0
