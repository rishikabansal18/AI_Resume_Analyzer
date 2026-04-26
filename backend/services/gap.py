def skill_gap(user_skills, job_skills):
    user_set = set(user_skills)
    job_set = set(job_skills)

    matched = list(user_set & job_set)
    missing = list(job_set - user_set)

    return matched, missing