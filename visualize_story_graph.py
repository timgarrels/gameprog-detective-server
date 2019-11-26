import json
from graphviz import Digraph

from config import Config


def main():

    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    story_graph = Digraph("Story")
    story_graph.attr('graph', forcelabels='True')

    # Add start Node
    story_graph.attr('node', shape='doublecircle')
    story_graph.node(story["story_start_point"])
    # Add Nodes
    story_graph.attr('node', shape='circle')
    for story_point in story["story_graph"].keys():
        story_graph.node(story_point)

    # Add edges
    for story_point, reply_dict in story["story_graph"].items():
        for reply, next_point in reply_dict.items():
            story_graph.edge(story_point, next_point, xlabel=reply)

    story_graph.view()
    

if __name__ == "__main__":
    main()
