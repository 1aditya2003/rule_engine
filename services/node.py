class Node:
    def __init__(self, node_type: str, value=None, left=None, right=None):
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        """ Convert node to a dictionary representation, omitting null values and unnecessary group nodes. """
        # Check if the node is a 'group' and can be simplified
        if self.node_type == 'group' and not self.value and not self.left and self.right:
            # If the group has no value and only a right child, simplify it to the right child
            return self.right.to_dict()

        # Otherwise, proceed normally
        result = {
            "node_type": self.node_type,
            "value": self.value
        }
        
        # Only add 'left' and 'right' if they exist (not None)
        if self.left:
            result["left"] = self.left.to_dict()
        if self.right:
            result["right"] = self.right.to_dict()

        # Remove any keys with None values
        return {k: v for k, v in result.items() if v is not None}

    
    def update_value(self, new_value):
        """ Update the value of the node """
        self.value = new_value

    def update_operator(self, new_operator):
        """ Change operator of the node """
        if self.node_type == 'operator':
            self.value = new_operator
        else:
            raise ValueError("Node is not an operator")