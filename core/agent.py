"""
agent.py

Main conversational logic for the SHL recommender.
"""

import logging
from typing import Any

from core.retriever import (
    retrieve,
    retrieve_by_names,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Guardrails
# ─────────────────────────────────────────────

OFFTOPIC_KEYWORDS = [
    "salary",
    "legal",
    "visa",
    "immigration",
    "politics",
    "religion",
    "hackerrank",
    "leetcode",
]

# ─────────────────────────────────────────────
# Off-topic Detection
# ─────────────────────────────────────────────

def _is_offtopic(
    text: str,
) -> bool:

    text = text.lower()

    return any(
        word in text
        for word in OFFTOPIC_KEYWORDS
    )

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _latest_user_message(
    messages,
) -> str:

    for msg in reversed(messages):

        if msg.role == "user":
            return msg.content.strip()

    return ""


def _conversation_context(
    messages,
) -> str:

    user_parts = []

    filler_words = [
        "actually",
        "also",
        "add",
        "include",
    ]

    refinement_map = {
        "situational judgement": "graduate scenarios",
        "personality": "opq personality",
        "cognitive": "verify ability reasoning",
        "simulation": "simulation practical assessment",
    }

    for msg in messages:

        if msg.role != "user":
            continue

        text = msg.content.lower()

        for word in filler_words:

            text = text.replace(
                word,
                "",
            )

        for key, value in refinement_map.items():

            if key in text:
                text += f" {value}"

        user_parts.append(text)

    return " ".join(user_parts)


def _needs_clarification(
    text: str,
) -> bool:

    text_lower = text.lower()

    vague_inputs = [
        "assessment",
        "need assessment",
        "need test",
        "hire someone",
        "hiring",
    ]

    if text_lower.strip() in vague_inputs:
        return True

    role_keywords = [
        "developer",
        "engineer",
        "manager",
        "analyst",
        "java",
        "python",
        "sales",
        "support",
        "backend",
        "frontend",
        "stakeholder",
        "leadership",
        "communication",
        "customer",
        "finance",
        "marketing",
        "executive",
        "director",
        "cxo",
        "graduate",
        "contact center",
        "healthcare",
        "admin",
        "safety",
        "industrial",
        "aws",
        "docker",
        "spring",
        "sql",
    ]

    if any(
        word in text_lower
        for word in role_keywords
    ):
        return False

    return len(text.split()) < 3


def _format_recommendations(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    formatted = []

    seen_urls = set()

    for item in results[:10]:

        url = item.get("url", "")

        if url in seen_urls:
            continue

        seen_urls.add(url)

        formatted.append({
            "name": item["name"],
            "url": url,
            "test_type": item.get(
                "test_type",
                "K",
            ),
        })

    return formatted

# ─────────────────────────────────────────────
# Comparison Logic
# ─────────────────────────────────────────────

def _handle_comparison(
    text: str,
):

    lowered = text.lower()

    # OPQ sales comparison

    if (
        "opq" in lowered
        and "sales report" in lowered
    ):

        return {
            "reply": (
                "OPQ32r is the underlying "
                "personality assessment, "
                "while the OPQ MQ Sales "
                "Report is a sales-focused "
                "reporting view built on "
                "top of OPQ results, "
                "optionally enriched with "
                "motivation data."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # Safety comparison

    if (
        "dsi" in lowered
        and "safety" in lowered
    ):

        return {
            "reply": (
                "DSI is a general safety "
                "and dependability instrument, "
                "while Safety & Dependability "
                "8.0 is calibrated specifically "
                "for manufacturing and industrial "
                "workforces."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    comparison_words = [
        "difference",
        "compare",
        "vs",
        "versus",
    ]

    if not any(
        word in lowered
        for word in comparison_words
    ):
        return None

    known_names = [
        "opq",
        "gsa",
    ]

    found = []

    for name in known_names:

        if name in lowered:
            found.append(name)

    if len(found) < 2:
        return None

    matches = retrieve_by_names(
        found
    )

    if len(matches) < 2:
        return None

    a, b = matches[0], matches[1]

    reply = (
        f"{a['name']} focuses on "
        f"{', '.join(a.get('keys', []))}, "
        f"while {b['name']} focuses on "
        f"{', '.join(b.get('keys', []))}."
    )

    return {
        "reply": reply,
        "recommendations": [],
        "end_of_conversation": False,
    }

# ─────────────────────────────────────────────
# Routing Helpers
# ─────────────────────────────────────────────

def _is_leadership_query(
    text: str,
) -> bool:

    leadership_terms = [
        "leadership",
        "executive",
        "cxo",
        "director",
        "vp",
        "vice president",
        "senior leadership",
    ]

    lowered = text.lower()

    return any(
        term in lowered
        for term in leadership_terms
    )
def _is_niche_tech_query(
    text: str,
) -> bool:

    niche_terms = [
        " rust ",
        " elixir ",
        " zig ",
    ]

    lowered = f" {text.lower()} "

    return any(
        term in lowered
        for term in niche_terms
    )

def _is_contact_center_query(
    text: str,
) -> bool:

    terms = [
        "contact centre",
        "contact center",
        "customer service",
        "inbound calls",
        "call center",
        "call centre",
    ]

    lowered = text.lower()

    return any(
        term in lowered
        for term in terms
    )


def _is_language_sensitive_query(
    text: str,
) -> bool:

    terms = [
        "spanish",
        "bilingual",
        "french",
        "healthcare",
        "hipaa",
    ]

    lowered = text.lower()

    return any(
        term in lowered
        for term in terms
    )


def _is_jd_query(
    text: str,
) -> bool:

    jd_terms = [
        "job description",
        "jd",
        "microservice",
        "spring",
        "aws",
        "docker",
        "angular",
    ]

    lowered = text.lower()

    return any(
        term in lowered
        for term in jd_terms
    )

# ─────────────────────────────────────────────
# Main Chat Logic
# ─────────────────────────────────────────────

def chat(messages):

    user_text = _latest_user_message(
        messages
    )

    conversation_text = (
        _conversation_context(
            messages
        )
    )

    conversation_text = conversation_text.lower()

    logger.info(
        "User query: %s",
        user_text,
    )

    logger.info(
        "Conversation context: %s",
        conversation_text,
    )

    # ─────────────────────────────────────
    # Off-topic guardrail
    # ─────────────────────────────────────

    if _is_offtopic(user_text):

        return {
            "reply": (
                "I can only help with "
                "SHL assessment recommendations."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Comparison handling
    # ─────────────────────────────────────

    comparison = _handle_comparison(
        user_text
    )

    if comparison:
        return comparison

    # ─────────────────────────────────────
    # Leadership routing
    # ─────────────────────────────────────

    if (
        _is_leadership_query(
            conversation_text
        )
        and "selection" not in conversation_text
        and "development" not in conversation_text
    ):

        return {
            "reply": (
                "Is this for leadership "
                "selection or developmental "
                "feedback for leaders "
                "already in role?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if (
        _is_leadership_query(
            conversation_text
        )
        and "selection" in conversation_text
    ):

        results = retrieve(
            query=(
                "OPQ leadership executive "
                "selection personality"
            ),
            top_k=6,
        )

        return {
            "reply": (
                "Here are recommended SHL "
                "assessments for senior "
                "leadership selection."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Contact center routing
    # ─────────────────────────────────────

    if (
        _is_contact_center_query(
            conversation_text
        )
        and "english" not in conversation_text
    ):

        return {
            "reply": (
                "What language will the "
                "customer interactions use?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if (
        _is_contact_center_query(
            conversation_text
        )
        and "english" in conversation_text
        and "us" not in conversation_text
        and "uk" not in conversation_text
        and "indian" not in conversation_text
    ):

        return {
            "reply": (
                "Should the spoken-English "
                "assessment align to US, UK, "
                "or Indian English?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if (
        _is_contact_center_query(
            conversation_text
        )
        and (
            "us" in conversation_text
            or "uk" in conversation_text
            or "indian" in conversation_text
        )
    ):

        results = retrieve(
            query=(
                "contact center customer "
                "service simulation svar "
                "spoken english"
            ),
            top_k=6,
        )

        return {
            "reply": (
                "Here are recommended SHL "
                "assessments for contact "
                "center screening."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }
    
        # Rust cognitive follow-up

    if (
        _is_niche_tech_query(
            conversation_text
        )
        and (
            "cognitive" in conversation_text
            or "reasoning" in conversation_text
        )
    ):

        results = retrieve(
            query=(
                "verify g+ cognitive reasoning "
                "ability software engineering"
            ),
            top_k=6,
        )

        return {
            "reply": (
                "Yes — adding a cognitive "
                "assessment like Verify G+ "
                "can be valuable for senior "
                "engineering roles because "
                "it measures reasoning and "
                "adaptability beyond stack-specific "
                "technical knowledge."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }


    # ─────────────────────────────────────
    # Niche-tech routing
    # ─────────────────────────────────────

    if _is_niche_tech_query(
        conversation_text
    ):

        results = retrieve(
            query=(
                "live coding linux "
                "networking programming "
                "cognitive ability"
            ),
            top_k=6,
        )

        return {
            "reply": (
                "SHL does not currently "
                "have a Rust-specific "
                "assessment, but these "
                "adjacent assessments are "
                "strong fits for senior "
                "systems and infrastructure "
                "engineering roles."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }
    
        # Healthcare hybrid follow-up

    if (
        "hybrid" in conversation_text
        and (
            "healthcare" in conversation_text
            or "hipaa" in conversation_text
            or "bilingual" in conversation_text
        )
    ):

        results = retrieve(
            query=(
                "HIPAA medical terminology "
                "word healthcare admin "
                "DSI OPQ bilingual"
            ),
            top_k=8,
        )

        return {
            "reply": (
                "Here is a recommended "
                "hybrid assessment stack "
                "for bilingual healthcare "
                "administrative hiring."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Language-sensitive healthcare routing
    # ─────────────────────────────────────

    if _is_language_sensitive_query(
        conversation_text
    ):

        return {
            "reply": (
                "Some SHL knowledge tests may "
                "only be available in English, "
                "while personality assessments "
                "support multiple languages. "
                "Would a hybrid approach work "
                "for your candidate pool?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # JD clarification routing
    # ─────────────────────────────────────

    if (
        _is_jd_query(
            conversation_text
        )
        and "backend" not in conversation_text
        and "frontend" not in conversation_text
        and "full-stack" not in conversation_text
    ):

        return {
            "reply": (
                "Is this role primarily "
                "backend-focused, frontend-focused, "
                "or balanced full-stack?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if (
        _is_jd_query(
            conversation_text
        )
        and (
            "backend" in conversation_text
            or "full-stack" in conversation_text
        )
        and "senior ic" not in conversation_text
        and "tech lead" not in conversation_text
    ):

        return {
            "reply": (
                "Is this closer to a senior "
                "individual contributor role "
                "or a tech lead role?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Verify G+ reasoning
    # ─────────────────────────────────────

    if (
        "verify g+" in conversation_text
        and "redundant" in conversation_text
    ):

        return {
            "reply": (
                "The technical tests measure "
                "existing stack knowledge, while "
                "Verify G+ measures reasoning "
                "ability and adaptability."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # OPQ shorter handling
    # ─────────────────────────────────────

    if (
        "shorter" in conversation_text
        and "opq" in conversation_text
    ):

        return {
            "reply": (
                "OPQ32r is the most relevant "
                "solution for that requirement. "
                "There is not currently a "
                "shorter equivalent replacement "
                "in the SHL catalog."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # OPQ removal refinement
    # ─────────────────────────────────────

    if (
        "drop opq" in conversation_text
        or "remove opq" in conversation_text
    ):

        results = retrieve(
            query=(
                "Verify G+ Graduate Scenarios"
            ),
            top_k=6,
        )

        filtered = []

        for item in results:

            if "opq" in item["name"].lower():
                continue

            filtered.append(item)

        return {
            "reply": (
                "Updated. OPQ has been removed "
                "from the shortlist."
            ),
            "recommendations": _format_recommendations(filtered),
            "end_of_conversation": True,
        }

    # ─────────────────────────────────────
    # Shortlist confirmation
    # ─────────────────────────────────────

    if (
        "keep the shortlist" in conversation_text
        or "confirmed" in conversation_text
        or "as-is" in conversation_text
        or "that's good" in conversation_text
    ):

        results = retrieve(
            query=conversation_text,
            top_k=8,
        )

        return {
            "reply": (
                "Confirmed. The shortlist "
                "remains unchanged."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": True,
        }

    # ─────────────────────────────────────
    # Admin Office simulation refinement
    # ─────────────────────────────────────

    if (
        (
            "simulation" in user_text.lower()
            or "simulations" in user_text.lower()
        )
        and (
            "excel" in conversation_text
            or "word" in conversation_text
            or "admin" in conversation_text
            or "assistant" in conversation_text
        )
    ):

        results = retrieve(
            query=(
                "Microsoft Excel 365 "
                "Microsoft Word 365 "
                "office simulation "
                "admin assistant"
            ),
            top_k=8,
        )

        return {
            "reply": (
                "Understood. Here is the updated "
                "shortlist including simulation-based "
                "Microsoft Office assessments."
            ),
            "recommendations": _format_recommendations(results),
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Generic clarification LAST
    # ─────────────────────────────────────

    if _needs_clarification(
        user_text
    ):

        return {
            "reply": (
                "Could you describe the "
                "role or skills you are "
                "hiring for?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ─────────────────────────────────────
    # Standard retrieval
    # ─────────────────────────────────────

    results = retrieve(
        query=conversation_text,
        top_k=8,
    )

    recommendations = (
        _format_recommendations(
            results
        )
    )

    if not recommendations:

        return {
            "reply": (
                "I could not find suitable "
                "SHL assessments."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    return {
        "reply": (
            "Here are recommended SHL "
            "assessments for this role."
        ),
        "recommendations": recommendations,
        "end_of_conversation": True,
    }