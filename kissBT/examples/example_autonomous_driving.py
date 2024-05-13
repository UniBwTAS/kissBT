from kissBT.core.behavior_tree import *
import random
import time

"""
Small Behavior Tree example for autonomous driving.

A vehicle is driving along a road. 
In case a static obstacle blocks the way, the ego vehicle dodges.
The dodging maneuver can take some time and results in a successful completion or a collision.
The task is completed when the ego vehicle has no remaining distance between itself and the goal.
"""

# =============================================================================
# --- Define nodes ------------------------------------------------------------
# =============================================================================

class Successor(Action):
    def __init__(self, name):
        super().__init__(name)
        # Add code if you need some things done at initialization

    def run(self):
        # Return either success, failure or running
        self.status = Status.SUCCESS


class RandomStatus(Condition):
    def __init__(self, name):
        super().__init__(name)
        # Add code if you need some things done at initialization

    def run(self):
        # Return either success or failure
        self.status = random.choice([Status.SUCCESS, Status.FAILURE])


class DodgeStaticObstacle(Action):
    def __init__(self, name):
        super().__init__(name)
        # Add code if you need some things done at initialization

    def run(self):
        # Return either success, failure or running
        random_number = random.randint(0, 4)
        if random_number in [1, 2]:
            self.status = Status.SUCCESS
        elif random_number in [3, 4]:
            # Do not use augmented assignment operators, e.g. "-=", as the write process becomes "invisible" for the activity logging.
            self.blackboard["distance_to_goal"] = self.blackboard["distance_to_goal"] - 0.5
            self.status = Status.RUNNING
        else:
            self.blackboard["failure_info"] = "Collision occurred!"
            self.status = Status.FAILURE


class FollowLane(Action):
    def __init__(self, name):
        super().__init__(name)
        # Add code if you need some things done at initialization

    def run(self):
        # Return either success, failure or running
        self.blackboard["distance_to_goal"] = self.blackboard["distance_to_goal"] - 1
        if self.blackboard["distance_to_goal"] <= 0:
            self.status = Status.SUCCESS
            self.blackboard["goal_reached"] = True
        else:
            self.status = Status.RUNNING

# =============================================================================
# --- Build tree --------------------------------------------------------------
# =============================================================================

# Define root -- Any node can be root node
root = Sequence("ROOT")

# Attach blackboard
my_blackboard = Blackboard()
my_blackboard["distance_to_goal"] = 5.0
my_blackboard["goal_reached"] = False
root.attach_blackboard(my_blackboard)

sel_dodge = Selector("Dodging")
dec_inv = Inverter("Inverter")
con_dodge = RandomStatus("StaticObstacleAhead")
dec_inv.set_child(con_dodge)
act_dodge = DodgeStaticObstacle("DodgeStaticObstacle")
sel_dodge.append(dec_inv)
sel_dodge.append(act_dodge)
root.append(sel_dodge)

act_follow = FollowLane("FollowLane")
root.append(act_follow)

# =============================================================================
# --- Execute tree ------------------------------------------------------------
# =============================================================================

while root.status not in [Status.FAILURE, Status.SUCCESS]:
    root.tick()
    print(root.get_string_tree())
    print("Remaining distance to goal :: ", my_blackboard["distance_to_goal"], "\n")
    time.sleep(1)

if root.status == Status.FAILURE:
    print(f"Mission failed!\nReason :: {my_blackboard['failure_info']}")
else:
    print("Goal reached!")

# =============================================================================
# --- Activity Steam ----------------------------------------------------------
# =============================================================================

print("\nACTIVITY STREAM")

# If you only want the write-accesses and key to be "distance_to_goal" and client "FollowLane", uncomment the following line
# print(my_blackboard.get_activity_str(mode="write", client="FollowLane", key="distance_to_goal"))

print(my_blackboard.get_activity_str())


