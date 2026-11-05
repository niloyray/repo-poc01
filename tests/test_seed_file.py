from app.seed import DEFAULT_SEED_PATH, parse_seed

NAMES = [
    "Knowledge graphs",
    "AI-native SDLC",
    "Business process modeling with agentic AI",
    "Problem solving",
    "Algorithms",
    "AI news of high importance",
    "New releases",
]


def test_shipped_file_has_the_seven_topics():
    topics = parse_seed(DEFAULT_SEED_PATH)
    assert [t["name"] for t in topics] == NAMES
    assert all(t["keywords"] for t in topics)


def test_lean_topic_is_the_theorem_prover():
    topic = parse_seed(DEFAULT_SEED_PATH)[3]
    assert "theorem prover" in topic["description"]
    assert {"lean manufacturing", "lean startup", "six sigma"} <= set(topic["exclusion_keywords"])
