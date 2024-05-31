import typing as tp
from collections import defaultdict

import community as community_louvain
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import requests
from vkapi.friends import get_friends, get_mutual


def ego_network(
    user_id: tp.Optional[int] = None, friends: tp.Optional[tp.List[int]] = None
) -> tp.List[tp.Tuple[int, int]]:
    """
    Построить эгоцентричный граф друзей.
    """
    graph = []
    if friends is None:
        friends = [user["id"] for user in get_friends(user_id=user_id).items if user.get(
            "deactivated") is None and not user.get("is_closed")]
    if user_id is not None:
        for friend in friends:
            graph.append((user_id, friend))
    mutual_friends = get_mutual(source_uid=user_id, target_uids=friends)
    for mutual in mutual_friends:
        graph.extend((mutual["id"], common)
                     for common in mutual["common_friends"] if mutual["id"] and common)
    return graph


def plot_ego_network(net: tp.List[tp.Tuple[int, int]], with_labels: bool = True) -> None:
    """
    Отрисовать эгоцентричный граф друзей.
    """
    graph = nx.Graph()
    graph.add_edges_from(net)
    layout = nx.spring_layout(graph)
    nx.draw(graph, layout, node_size=10, node_color="black", alpha=0.5)
    if with_labels:
        nx.draw_networkx_labels(graph, layout, font_size=8)
    plt.title("Ego Network", size=15)
    plt.show()


def plot_communities(net: tp.List[tp.Tuple[int, int]]) -> None:
    graph = nx.Graph()
    graph.add_edges_from(net)
    layout = nx.spring_layout(graph)
    partition = community_louvain.best_partition(graph)
    nx.draw(graph, layout, node_size=25, node_color=list(
        partition.values()), alpha=0.8, cmap=plt.cm.Rainbow)
    plt.title("Ego Network Communities", size=15)
    plt.show()


def get_communities(net: tp.List[tp.Tuple[int, int]]) -> tp.Dict[int, tp.List[int]]:
    graph = nx.Graph()
    graph.add_edges_from(net)
    partition = community_louvain.best_partition(graph)
    communities = defaultdict(list)
    for uid, cluster in partition.items():
        communities[cluster].append(uid)
    return communities


def describe_communities(
    clusters: tp.Dict[int, tp.List[int]],
    friends: tp.List[tp.Dict[str, tp.Any]],
    fields: tp.Optional[tp.List[str]] = None,
) -> pd.DataFrame:
    if fields is None:
        fields = ["first_name", "last_name"]

    data = [
        [cluster_n] + [friend.get(field) for field in fields]
        for cluster_n, cluster_users in clusters.items()
        for uid in cluster_users
        for friend in friends
        if uid == friend["id"]
    ]
    return pd.DataFrame(data=data, columns=["cluster"] + fields)
