"""
awareness_engine.py
===================
Delivers age-appropriate drug awareness content and quizzes.
Covers effects, withdrawal timelines, real statistics, and myth-busting.
"""

from typing import Dict, List, Optional
import random


AWARENESS_CONTENT = {
    "effects": {
        "teen": {
            "title": "What Drugs Actually Do to Your Brain",
            "content": (
                "Your brain is still developing until age 25. Drugs hijack your brain's "
                "reward system — flooding it with dopamine. Over time, your brain stops "
                "producing natural happiness, making you dependent on the substance just to feel normal. "
                "Teens who use drugs are 4x more likely to develop addiction than adults."
            ),
            "did_you_know": "Even 'trying once' can trigger changes in brain chemistry for some people.",
            "stat": "70% of adults with addiction started using before age 18.",
        },
        "young_adult": {
            "title": "The Science of Addiction",
            "content": (
                "Addiction is a chronic brain disorder — not a moral failing. "
                "Repeated substance use rewires the prefrontal cortex (decision-making) "
                "and the limbic system (emotions and reward). This creates compulsive use "
                "even when the person wants to stop. Recovery is possible and the brain can heal."
            ),
            "did_you_know": "The brain's neuroplasticity means recovery is always possible, even after years of use.",
            "stat": "Only 10% of people with addiction receive treatment — stigma is the biggest barrier.",
        },
        "adult": {
            "title": "Addiction, the Brain, and Recovery",
            "content": (
                "Long-term substance use causes structural changes in the brain, particularly "
                "in areas controlling impulse, stress, and reward. Evidence-based treatments "
                "like CBT, MAT, and peer support show 40–60% long-term recovery rates — "
                "comparable to other chronic diseases like diabetes and hypertension."
            ),
            "did_you_know": "Relapse is part of recovery for many people — it doesn't mean failure.",
            "stat": "India has an estimated 14.6 million substance users needing treatment intervention.",
        },
    },
    "withdrawal": {
        "teen": {
            "title": "What Happens When You Stop?",
            "content": (
                "Stopping drugs can cause withdrawal — your body adjusting to not having the substance. "
                "This might feel like the flu, anxiety, or restlessness. It's temporary. "
                "The first 3–7 days are usually the hardest. After that, it gets better every day."
            ),
        },
        "young_adult": {
            "title": "Withdrawal Timelines by Substance",
            "content": (
                "• Alcohol: Symptoms begin 6–24 hrs, peak 24–72 hrs, can be dangerous — see a doctor.\n"
                "• Cannabis: Irritability & insomnia for 1–2 weeks, mostly psychological.\n"
                "• Opioids: 'Flu-like' symptoms peaking at 36–72 hrs. MAT (medication-assisted treatment) helps greatly.\n"
                "• Stimulants: Fatigue and depression for 1–2 weeks, no physical danger.\n"
                "• Tobacco: Nicotine withdrawal peaks at 2–3 days, mostly manageable with NRT."
            ),
        },
        "adult": {
            "title": "Medical Management of Withdrawal",
            "content": (
                "Medically supervised detox is recommended for alcohol, benzodiazepines, and opioids "
                "due to risk of seizures or severe decompensation. "
                "Medication-Assisted Treatment (MAT) with buprenorphine or methadone for opioids "
                "has the strongest evidence base for retention in treatment and reduced mortality."
            ),
        },
    },
    "myths": {
        "teen": {
            "title": "Myths vs Facts",
            "content": (
                "❌ MYTH: 'Everyone is doing it.'\n✅ FACT: 80%+ of teens have never used drugs.\n\n"
                "❌ MYTH: 'I can stop whenever I want.'\n✅ FACT: Addiction physically changes the brain — stopping takes real support.\n\n"
                "❌ MYTH: 'Weed is completely harmless.'\n✅ FACT: Regular use in teens is linked to memory issues and lower academic performance."
            ),
        },
        "young_adult": {
            "title": "Common Myths About Addiction",
            "content": (
                "❌ MYTH: 'Addiction is a choice or weakness.'\n✅ FACT: It's a chronic brain disease recognized by WHO and all major medical bodies.\n\n"
                "❌ MYTH: 'You have to hit rock bottom before getting help.'\n✅ FACT: Earlier intervention = better outcomes. You can seek help today.\n\n"
                "❌ MYTH: 'Medication-assisted treatment is just replacing one drug with another.'\n✅ FACT: MAT is evidence-based and dramatically improves recovery rates."
            ),
        },
        "adult": {
            "title": "Stigma and Addiction",
            "content": (
                "Stigma — including self-stigma — is the single biggest barrier to seeking treatment. "
                "People with addiction are not 'junkies' or morally weak; they are people with a medical condition. "
                "Using person-first language ('person with addiction' not 'addict') matters. "
                "Empathy and non-judgment improve treatment engagement dramatically."
            ),
        },
    },
}

QUIZZES = {
    "teen": [
        {
            "question": "At what age does the human brain fully develop?",
            "options": ["18", "21", "25", "30"],
            "answer": "25",
            "explanation": "The prefrontal cortex — responsible for decisions and impulse control — develops until about age 25.",
        },
        {
            "question": "Which of these is TRUE about addiction?",
            "options": [
                "It's a sign of weak willpower",
                "It only affects 'certain types' of people",
                "It's a chronic brain disease",
                "One try is always safe",
            ],
            "answer": "It's a chronic brain disease",
            "explanation": "Addiction is recognized by WHO as a chronic brain disorder — not a character flaw.",
        },
        {
            "question": "What percentage of teens have NEVER used drugs?",
            "options": ["30%", "50%", "65%", "80%+"],
            "answer": "80%+",
            "explanation": "Despite what movies show, the majority of teenagers do not use drugs.",
        },
    ],
    "young_adult": [
        {
            "question": "Which substance has the most dangerous withdrawal?",
            "options": ["Cannabis", "Alcohol", "Tobacco", "Stimulants"],
            "answer": "Alcohol",
            "explanation": "Alcohol withdrawal can cause life-threatening seizures. Always detox under medical supervision.",
        },
        {
            "question": "What does MAT stand for in addiction treatment?",
            "options": [
                "Mental Awareness Training",
                "Medication-Assisted Treatment",
                "Mindfulness and Therapy",
                "Medical Addiction Test",
            ],
            "answer": "Medication-Assisted Treatment",
            "explanation": "MAT uses medications like buprenorphine to manage cravings and withdrawal, especially for opioids.",
        },
    ],
    "adult": [
        {
            "question": "Recovery success rates for addiction are comparable to which other chronic disease?",
            "options": ["Cancer", "Diabetes", "HIV", "Alzheimer's"],
            "answer": "Diabetes",
            "explanation": "Addiction treatment has 40–60% long-term success rates, similar to diabetes and hypertension management.",
        },
    ],
}


class AwarenessEngine:

    def get_content(
        self, topic: str, age_group: str, substance: Optional[str] = None
    ) -> Dict:
        """Returns educational content for a given topic and age group."""
        topic_data = AWARENESS_CONTENT.get(topic, {})
        content = topic_data.get(age_group, topic_data.get("young_adult", {}))

        return {
            "topic": topic,
            "age_group": age_group,
            "substance": substance,
            **content,
            "helpline": "iCall India — 9152987821 (Free, confidential counseling)",
        }

    def get_quiz(self, age_group: str) -> List[Dict]:
        """Returns a randomized quiz for the given age group."""
        questions = QUIZZES.get(age_group, QUIZZES["young_adult"])
        # Shuffle options for each question
        result = []
        for q in questions:
            shuffled = q["options"][:]
            random.shuffle(shuffled)
            result.append({**q, "options": shuffled})
        return result
