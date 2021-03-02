def beautify(name: str, repos_dict: dict) -> str:
    """TODO"""
    heading = f"\n{name:<40}stars forks\n" + ("=" * 51)

    starforks_str = ""
    for repo, info in repos_dict.items():
        starforks_str += f"\n{repo:<40} {info['stars']:4}  {info['forks']:4}"

    return heading + starforks_str + "\n"