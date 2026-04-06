import random

def generate_smart_recommendation(attendance, avg_marks, backlogs):

    # ================= LOW PERFORMANCE =================
    low_perf = [
        [
            f"Right now, your attendance is around {attendance:.1f}%, which is clearly affecting your understanding of subjects. If you continue missing classes, it will become very hard to recover later.",
            f"Your average marks are {avg_marks:.1f}, which shows that your fundamentals are not strong yet. Instead of rushing topics, focus on understanding concepts slowly and clearly.",
            "Start watching structured YouTube lectures like Gate Smashers or Neso Academy and follow them consistently instead of random videos.",
            "After every topic, solve a few basic problems to reinforce your understanding instead of just reading theory.",
            f"You currently have {backlogs} backlogs, and ignoring them will only increase pressure later, so start clearing them one by one.",
            "Make a simple daily plan of 2–3 hours and follow it consistently rather than studying randomly."
        ],
        [
            f"Your attendance ({attendance:.1f}%) and marks ({avg_marks:.1f}) indicate that you are falling behind in multiple subjects.",
            "At this stage, the goal should not be scoring high marks but building a strong base in each subject.",
            "Use platforms like GeeksforGeeks or Tutorialspoint to understand topics in a simple way before moving to advanced materials.",
            "Try to revise whatever you study on the same day, because delayed revision leads to forgetting.",
            f"Since you have {backlogs} backlog subjects, divide them across weeks instead of trying to handle everything at once.",
            "Avoid last-minute studying completely — consistency is the only way out here."
        ]
    ]

    # ================= MEDIUM PERFORMANCE =================
    medium_perf = [
        [
            f"Your attendance is around {attendance:.1f}%, which is decent but still not enough to maximize your performance.",
            f"With an average of {avg_marks:.1f} marks, you are in a stable position but there is clear room for improvement.",
            "Instead of just attending classes, start actively engaging with the subject by solving problems regularly.",
            "Practice previous year question papers to understand the exam pattern and important topics.",
            "Use platforms like LeetCode or HackerRank to strengthen your problem-solving skills gradually.",
            "If you stay consistent with revision and practice, you can easily move to a higher performance level."
        ],
        [
            f"Looking at your attendance ({attendance:.1f}%) and marks ({avg_marks:.1f}), you are doing okay but not at your full potential.",
            "At this level, small improvements in consistency can make a big difference in your results.",
            "Focus more on applying concepts rather than just reading them, because application builds confidence.",
            "Set weekly goals for each subject instead of studying randomly without direction.",
            "Track your weak areas and spend extra time on them instead of repeatedly studying what you already know.",
            "With a bit more discipline, you can easily push your performance to the next level."
        ]
    ]

    # ================= HIGH PERFORMANCE =================
    high_perf = [
        [
            f"Your attendance is {attendance:.1f}%, which shows strong consistency and discipline in your academic routine.",
            f"With an average of {avg_marks:.1f}, you are already performing well compared to most students.",
            "At this stage, you should shift your focus from basic understanding to mastering advanced concepts.",
            "Start working on real-world projects or mini applications to apply what you have learned.",
            "Practice advanced problems on platforms like LeetCode to sharpen your thinking and problem-solving ability.",
            "If you continue this level of consistency, you can aim for top ranks and strong placement opportunities."
        ],
        [
            f"Your current performance, with {attendance:.1f}% attendance and {avg_marks:.1f} marks, is already strong.",
            "Now the goal should be to stand out rather than just maintaining this level.",
            "Focus on deeper understanding of subjects and explore topics beyond the syllabus.",
            "Participate in coding contests, hackathons, or technical events to challenge yourself.",
            "Building projects and showcasing them will give you an edge during placements.",
            "Keep pushing your limits, because this is the stage where you can really differentiate yourself."
        ]
    ]

    # ================= SELECT =================
    if avg_marks < 40 or attendance < 60:
        return random.choice(low_perf)

    elif avg_marks < 60 or attendance < 75:
        return random.choice(medium_perf)

    else:
        return random.choice(high_perf)