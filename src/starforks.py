import sys
import csv
from pathlib import Path
from datetime import date
from typing import Optional, Union
from cycler import cycler

import numpy as np
import matplotlib.pyplot as plt
from github import Github

class Connection():
    """Connects to the GitHub API and provides access to public repositories
    and statistics.

    Args:
        access_token (str)
    """

    def __init__(self, access_token: str) -> None:
        self.g = Github(access_token)

    def get_repos(self, name: str) -> list:
        """Get public repositories from organization.

        Args:
            name (str): name of organization

        Returns:
            list[str]: list of repository names
        """
        organization = self.g.get_organization(name)
        return [org.name for org in organization.get_repos()]

    def get_data(self, name: str) -> dict:
        """Retrieves number of stars and forks for each public repository in an
        organization.

        Args:
            name (str): name of organization

        Returns:
            dict[str, list]: dictionary containing three entries/lists:
                repository names, GitHub stars and GitHub forks
        """
        organization = self.g.get_organization(name)

        data = [
            (repo.name, repo.stargazers_count, repo.forks_count)
            for repo in organization.get_repos()
        ]

        fieldnames, stars, forks = zip(*data)
        data_dict = {
            "organization": name,
            "repository_names": fieldnames,
            "stars": stars,
            "forks": forks
            }

        return data_dict

    def write_data(self, data: dict) -> None:
        """Writes data to csv files. Two files for each organization: one with stars
        and one with forks.

        Args:
            data [dict]: "organization", "repository_names", "stars" and "forks" as keys,
                and lists of correspondning data as values
        """
        organization = data.pop("organization")
        fieldnames = data.pop("repository_names")

        datapath = Path("data")
        for d_type, d in data.items():
            filename = f"{organization.lower()}_{d_type}.csv"
            datapath.mkdir(parents=True, exist_ok=True)

            filepath = datapath / filename
            file_exists = filepath.exists()

            # open(file) creates file if it doesn't exist; check first
            csvfile = open(filepath, "a", newline="")

            w = csv.writer(csvfile)
            if not file_exists:
                w.writerow(("",) + fieldnames)

            w.writerow((str(date.today()),) + d)

            csvfile.close()

    def update(self) -> None:
        """Downloads and adds new data to the csv data files for each organization."""
        for organization in ["PennyLaneAI", "XanaduAI"]:
            data = self.get_data(organization)
            self.write_data(data)


def load_data(
    organization: Union[str, list] = "all",
    repositories: Union[str, list] = "all",
    d_type: Union[str, list] = "all"
) -> dict:
    """TODO"""
    if organization == "all":
        organization = ["PennyLaneAI", "XanaduAI"]
    elif isinstance(organization, str):
        organization = [organization]

    if d_type == "all":
        d_type = ["stars", "forks"]
    elif isinstance(d_type, str):
        d_type = [d_type]

    datapath = Path("data")
    data = dict()
    for t in d_type:
        data[t] = dict()
        for org in organization:
            data[t][org] = dict()

            filename = f"{org.lower()}_{t}.csv"
            filepath = datapath / filename

            if not filepath.exists():
                print("File does not exits. No data loaded!")
                return {}

            csvfile = open(filepath, "r")

            fieldnames = csvfile.readline().split(",")[1:]
            data_as_str = [d.strip().split(",") for d in csvfile.readlines()]
            data_as_str_numpy = np.array(data_as_str).T

            data[t][org]["time"] = data_as_str_numpy[0]

            for i, fn in enumerate(fieldnames):
                if repositories != "all" and fn not in repositories:
                    continue
                data[t][org][fn] = data_as_str_numpy[i + 1].astype(int)

    return data

def save_plots(data: dict, title: str="", filename: str="plot") -> None:
    """TODO"""
    fig, ax = plt.subplots()

    # use enough colour/linestyle combinations to get a new for each repo
    colours = [
        "xkcd:purple",
        "xkcd:green",
        "xkcd:brown",
        "xkcd:red",
        "xkcd:blue",
        "xkcd:pink",
        "xkcd:orange",
        "xkcd:magenta",
        "xkcd:yellow",
        "xkcd:grey",
        "xkcd:forest green",
        "xkcd:turquoise",
        "xkcd:cyan",
        "xkcd:periwinkle"
    ]
    new_prop_cycle = (
        cycler(linestyle=["-", ":", "--", "-."]) *
        cycler(color=colours)
    )

    for d_type, vals in data.items():
        # set the prop cycle for each fig
        ax.set_prop_cycle(new_prop_cycle)

        n_plots = 0
        for organization, data_list in vals.items():
            for k, v in data_list.items():
                if k != "time":
                    ax.plot(data_list["time"], v, label=k)
                    n_plots += 1

        # decide font size and number of columns in legend depending on the
        # number of plotted repositories
        if n_plots < 17:
            # 1 col with max 16 repos
            fontsize = 'medium'
            ncol = 1
        elif n_plots < 49:
            # 2 cols with max 24 in each
            fontsize = 'x-small'
            ncol = 2
        else:
            # 3+ cols with max 28 in each
            fontsize = 'xx-small'
            ncol = n_plots // 29 + 1

        ax.legend(
            frameon=False,
            bbox_to_anchor=(1.1, 1),
            loc='upper left',
            fontsize=fontsize,
            ncol=ncol
        )
        ax.set_ylabel = d_type
        fig.suptitle(title + f"  /  {d_type.capitalize()}")

        fig.set_size_inches(10, 5)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.75 - 0.10*ncol, top=0.9)
        fig.savefig(f"plots/{filename}_{d_type}.png")

        plt.cla()


def update_plots() -> None:
    """TODO"""
    plt.style.use('ggplot')

    pl_and_sf_data = load_data(repositories=["pennylane", "strawberryfields"])
    save_plots(pl_and_sf_data, title="PennyLane & Strawberry Fields", filename="pl_sf")

    all_repos_data = load_data()
    save_plots(all_repos_data, title="GitHub Repos", filename="all_repos")


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        raise SystemExit(
            "To update database you need to supply your GitHub authentication token:\n"
            "python starforks.py -t [GITHUB AUTHENTICATION TOKEN]"
        )

    elif sys.argv[1] == "-t":
        ACCESS_TOKEN = sys.argv[2]

        connection = Connection(ACCESS_TOKEN)
        connection.update()

        update_plots()
