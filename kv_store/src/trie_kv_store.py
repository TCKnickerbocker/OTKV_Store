# trie_kv_store.py
# A basic tree structure for kv storage
import threading

class TrieNode:
    def __init__(self):
        """Initialize a node in the trie"""
        self.children = {}  # Maps characters to child nodes
        self.value = None   # Stores value if this node represents end of a key
        self.is_end = False # Indicates if this node represents end of a key
        self.lock = threading.Lock()  # For thread-safe operations

class KVStore:
    def __init__(self):
        """Initialize an empty trie-based key-value store"""
        self.root = TrieNode()
        self.size = 0
        self.size_lock = threading.Lock()

    def set(self, key, value, **kwargs):
        """
        Set a value in the trie
        
        Args:
            key (str): The key to store
            value (any): The value to store
            **kwargs: Additional arguments (maintained for compatibility)
            
        Returns:
            int: 0 on success
        """
        if not isinstance(key, str):
            key = str(key)
            
        current = self.root
        
        # Traverse/build the trie path for this key
        for char in key:
            with current.lock:
                if char not in current.children:
                    current.children[char] = TrieNode()
                current = current.children[char]
        
        # Set the value at the final node
        with current.lock:
            was_new_key = not current.is_end
            current.value = value
            current.is_end = True
            
        # Update size if this was a new key
        if was_new_key:
            with self.size_lock:
                self.size += 1
                
        return 0

    def get(self, key):
        """
        Get a value from the trie
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            any: The stored value or None if key doesn't exist
        """
        if not isinstance(key, str):
            key = str(key)
            
        current = self.root
        
        # Traverse the trie to find the key
        for char in key:
            if char not in current.children:
                return "-1"
            current = current.children[char]
            
        return current.value if current.is_end else "-1"

    def delete(self, key):
        """
        Delete a key from the trie
        
        Args:
            key (str): The key to delete
            
        Returns:
            list: List containing 1 if key was deleted, -1 if key didn't exist
        """
        if not isinstance(key, str):
            key = str(key)
            
        def _delete_helper(node, key, depth):
            # Base case - reached end of key
            if depth == len(key):
                if not node.is_end:
                    return False
                with node.lock:
                    node.is_end = False
                    node.value = None
                return True
            
            char = key[depth]
            if char not in node.children:
                return False
            
            was_deleted = _delete_helper(node.children[char], key, depth + 1)
            
            # Clean up empty nodes
            if was_deleted:
                child = node.children[char]
                if not child.children and not child.is_end:
                    with node.lock:
                        del node.children[char]
            
            return was_deleted

        was_deleted = _delete_helper(self.root, key, 0)
        if was_deleted:
            with self.size_lock:
                self.size -= 1
            return [1]
        return [-1]

    def keys(self, pattern="*"):
        """
        Get all key-value pairs from the store
        
        Returns:
            dict: Dictionary containing all key-value pairs in the store
        """
        def _collect_pairs(node, prefix, store_dict):
            # If this node represents a key's end, add it to our dictionary
            if node.is_end:
                store_dict[prefix] = node.value
                
            # Recursively traverse all children
            for char, child in node.children.items():
                _collect_pairs(child, prefix + char, store_dict)

        if pattern == "*":  # Get entire contents of store
            # Dictionary to store all key-value pairs
            store_contents = {}
            
            # Start collection from root with empty prefix
            _collect_pairs(self.root, "", store_contents)
            
            return store_contents
        else:
            raise NotImplemented

# Create singleton instance
kv_store = KVStore()
