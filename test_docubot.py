"""
Simple, dependency-free test cases for build_index and score_document.

Run with:
    python test_docubot.py
"""

from docubot import DocuBot


def make_bot():
    # Bypass __init__ (which reads from disk) so we can test methods
    # in isolation with hand-crafted sample data.
    return object.__new__(DocuBot)


SAMPLE_DOCS = [
    ("AUTH.md", "Users authenticate with a token. The token expires after login."),
    ("DATABASE.md", "The database stores users and sessions in a table."),
    ("API_REFERENCE.md", "Send the token in the Authorization header."),
]


def test_build_index_basic():
    bot = make_bot()
    index = bot.build_index(SAMPLE_DOCS)

    assert "token" in index
    assert set(index["token"]) == {"AUTH.md", "API_REFERENCE.md"}
    assert index["database"] == ["DATABASE.md"]
    print("test_build_index_basic passed")


def test_build_index_lowercases_and_strips_punctuation():
    bot = make_bot()
    docs = [("A.md", "Token. TOKEN, token!")]
    index = bot.build_index(docs)

    assert "token" in index
    assert index["token"] == ["A.md"]
    # punctuation-only tokens like "." should not appear as keys
    assert "." not in index
    assert "," not in index
    print("test_build_index_lowercases_and_strips_punctuation passed")


def test_build_index_no_duplicate_filenames():
    bot = make_bot()
    docs = [("A.md", "token token token")]
    index = bot.build_index(docs)

    assert index["token"] == ["A.md"]  # not ["A.md", "A.md", "A.md"]
    print("test_build_index_no_duplicate_filenames passed")


def test_build_index_empty_documents():
    bot = make_bot()
    assert bot.build_index([]) == {}
    print("test_build_index_empty_documents passed")


def test_score_document_counts_matches():
    bot = make_bot()
    text = "The token expires after login. Token issued at login."
    score = bot.score_document("token login", text)

    # "token" appears 2x, "login" appears 2x -> score should be 4
    assert score == 4, f"expected 4, got {score}"
    print("test_score_document_counts_matches passed")


def test_score_document_no_match():
    bot = make_bot()
    text = "Completely unrelated content about databases."
    score = bot.score_document("authentication token", text)

    assert score == 0
    print("test_score_document_no_match passed")


def test_score_document_case_insensitive():
    bot = make_bot()
    text = "TOKEN token ToKeN"
    score = bot.score_document("Token", text)

    assert score == 3
    print("test_score_document_case_insensitive passed")


def test_score_document_different_queries_give_different_scores():
    bot = make_bot()
    text = "Authentication uses a token. The token is sent in a header."

    score_a = bot.score_document("token", text)
    score_b = bot.score_document("authentication token header", text)

    assert score_b > score_a
    print("test_score_document_different_queries_give_different_scores passed")


if __name__ == "__main__":
    test_build_index_basic()
    test_build_index_lowercases_and_strips_punctuation()
    test_build_index_no_duplicate_filenames()
    test_build_index_empty_documents()
    test_score_document_counts_matches()
    test_score_document_no_match()
    test_score_document_case_insensitive()
    test_score_document_different_queries_give_different_scores()
    print("\nAll tests passed!")
