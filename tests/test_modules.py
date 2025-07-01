import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import os
import tempfile

import Modules.AnimatedEvent as AnimatedEvent
import Modules.Checklist as Checklist
import Modules.Guide as Guide
import Modules.PDF as PDF


def test_pdf_repr():
    pdf = PDF.PDF('example.pdf')
    assert 'example.pdf' in pdf._repr_html_()


def test_guide_list_entries():
    entries = Guide.list_entries(print_list=False)
    assert isinstance(entries, list)
    assert len(entries) > 0


def test_checklist_list_notebooks():
    # Should not raise exceptions and should print available notebooks
    Checklist.Checklist.list_notebooks()


def test_animated_event(tmp_path):
    output_name = 'test.gif'
    AnimatedEvent.create_lens_animation(
        M=1.0,
        mu=1.0,
        Dl=1.0,
        Ds=2.0,
        output_file=output_name,
        save_path=str(tmp_path) + '/'  # path must end with /
    )
    assert (tmp_path / output_name).exists()
