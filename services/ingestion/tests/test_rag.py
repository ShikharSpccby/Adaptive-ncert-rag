import json

import pymupdf

from rag.chunking import chunk_by_structure, make_chunks, split_sentences
from rag.cli import ingest, main
from rag.config import load_config, parse_set_args

SAMPLE = """Triangles are closed figures with three sides. The sum of angles is 180 degrees. A side measures 2.5 cm here.

THEOREM 6.1 If a line is drawn parallel to one side of a triangle, it divides the other two sides in the same ratio. This is the basic proportionality theorem.

Proof : Draw lines and compare areas of the two triangles.

EXAMPLE 1 Find x if the sides are in proportion 2 : 3.

Solution : Cross multiply to get 3x = 12, so x = 4.

EXERCISE 6.1 1. Check whether two triangles are similar."""


def test_sentence_split_keeps_decimals():
    assert any("2.5 cm" in s for s in split_sentences(SAMPLE))


def test_structure_keeps_proof_with_theorem_and_solution_with_example():
    blocks = dict((k, t) for t, k in chunk_by_structure(SAMPLE))
    assert "Draw lines" in blocks["theorem"]
    assert "x = 4" in blocks["example"]


def test_strategy_and_size_are_config_driven():
    cfg = load_config()["chunking"]
    few = make_chunks(SAMPLE, {**cfg, "strategy": "sentence", "sentences_per_chunk": 6, "overlap": 0})
    many = make_chunks(SAMPLE, {**cfg, "strategy": "sentence", "sentences_per_chunk": 1, "overlap": 0})
    assert len(many) > len(few)


def test_set_overrides_parse_with_types():
    o = parse_set_args(["retrieval.top_k=8", "retrieval.filters={class_level: 10}"])
    assert o == {"retrieval": {"top_k": 8, "filters": {"class_level": 10}}}


def test_end_to_end_with_fake_embedder(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pdfs").mkdir()
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_textbox(pymupdf.Rect(40, 40, 550, 800), SAMPLE, fontsize=10)
    doc.save(str(tmp_path / "pdfs" / "class10_ch06_triangles.pdf"))
    over = ["data.pdf_dir=pdfs", "vector_store.path=db", "embedding.provider=fake",
            "generation.provider=echo", "retrieval.top_k=3"]
    flags = [x for o in over for x in ("--set", o)]
    main(["ingest", *flags])
    main(["query", "basic proportionality theorem parallel line ratio", *flags])
    out = capsys.readouterr().out
    assert "theorem" in out and "class_level" in out and "ANSWER" in out
    # metadata filter narrows results
    main(["query", "triangle", *flags, "--set", "retrieval.filters={class_level: 9}"])
    assert "Nothing retrieved" in capsys.readouterr().out
