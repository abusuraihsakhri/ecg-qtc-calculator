"""Formula and CSV safety regression tests."""
import csv
import pytest
from qtc import calculate_qtc, classify_qtc, qtc_framingham, rr_from_hr, process_csv

def test_framingham_units():
    assert qtc_framingham(350,600) == pytest.approx(411.6)
    assert qtc_framingham(420,1200) == pytest.approx(389.2)
    assert calculate_qtc(350,hr_bpm=100)["qtc_framingham"] == 411.6

@pytest.mark.parametrize("invalid",[float("nan"),float("inf"),float("-inf"),0,-1])
def test_bad_qt(invalid):
    with pytest.raises(ValueError): calculate_qtc(invalid,rr_ms=800)

def test_invalid_sex_at_high_qtc():
    with pytest.raises(ValueError): classify_qtc(550,"invalid")

def test_invalid_rate():
    for value in (float("nan"),float("inf"),-1,0):
        with pytest.raises(ValueError): rr_from_hr(value)

def test_csv_escape(tmp_path):
    source=tmp_path/"data.csv"
    output=tmp_path/"output.csv"
    source.write_text('patient_id,qt_ms,rr_ms\n"=1+1",350,600\n',encoding="utf-8")
    rows=process_csv(source,output)
    assert rows[0]["qtc_framingham"] == 411.6
    with output.open(newline="") as f:
        assert list(csv.DictReader(f))[0]["patient_id"]=="'=1+1"
    with pytest.raises(ValueError): process_csv(source,source)
