# Simple Behavior Tree

This is a very basic Behavior Tree implementation for Python. 
In case you're searching for a BT library with rich features, we recommend you take a look at [py_trees](https://py-trees.readthedocs.io/en/devel/index.html).
However, if you want a basic library where you can easily understand the overall behavior or want to change some behavior/code without digging too deep, you might be served well here.

### Included

The [implementation](behavior_tree/core/behavior_tree.py) provides:

- Nodes
  - Control nodes
    - Sequence
    - Selector
    - ParallelSequence 
  - Leaves
    - Conditions
    - Actions
  - Decorators
    - Inverter
- Unicode Behavior Tree
  - Tree structure
  - Status feedback (with color)
  - Highlighting of running actions

``` 
[⦿][→] ROOT
 ┊   [⦿][?] Dodging
 ┊    ┊   [⦿][δ] Inverter
 ┊    ┊    ┊   [⦿] <StaticObstacleAhead>?
 ┊    ┊   [ ] DodgeStaticObstacle
 ┊   [⦿] FollowLane <---- RUNNING
```

- Blackboard

### Example

You can find a small example [here](behavior_tree/examples/example_autonomous_driving.py).

### Final Words

If you have any ideas/suggestions on how to improve this project while keeping it simple, I would be glad if you share your opinion with me.