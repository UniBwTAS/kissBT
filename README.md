# kissBT: A Very Basic Behavior Tree Framework


This is a very basic Behavior Tree framework for Python. 
In case you're searching for a BT library with rich features, we recommend you take a look at [py_trees](https://py-trees.readthedocs.io/en/devel/index.html).
However, if you want a basic library where you can easily understand the overall behavior or want to change some behavior/code without digging too deep, you might be served well here.

### Installation

Install kissBT via the following command:

```bash
pip3 install git+https://github.com/UniBwTAS/kissBT.git#egg=kissBT
```

or

```bash
python3 -m pip install git+https://github.com/UniBwTAS/kissBT.git#egg=kissBT
```


### Included

The [implementation](kissBT/core/behavior_tree.py) provides:

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
  - Activity monitoring

```
>> WRITE [FollowLane].......... distance_to_goal : 1.0
>> READ  [FollowLane].......... distance_to_goal
>> READ  [<<NoMember>>]........ distance_to_goal
>> READ  [FollowLane].......... distance_to_goal
>> WRITE [FollowLane].......... distance_to_goal : 0.0
>> READ  [FollowLane].......... distance_to_goal
>> WRITE [FollowLane].......... goal_reached : True
```

### Example

You can find a small example [here](kissBT/examples/example_autonomous_driving.py).

### Final Words

If you have any ideas/suggestions on how to improve this project while keeping it simple, I would be glad if you share your opinion with me.
